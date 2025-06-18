import json
from os import makedirs, environ as ENV
from os.path import basename, join
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from xhtml2pdf import pisa


class MatchEvent(BaseModel):
    minute: int
    half: int
    event_type: str
    team_name: str
    player_name: str = None
    related_player_name: str = None
    commentary: str


class MatchPeriodSummary(BaseModel):
    period: str
    key_stats: str
    commentary: str


class MatchReport(BaseModel):
    match_title: str
    final_score: str
    match_date: str
    competition: str
    season: str
    match_summary: str
    period_summaries: list[MatchPeriodSummary]
    key_events: list[MatchEvent]
    final_thoughts: str


def get_db_connection(config: dict) -> connection:
    """Creates and returns a connection to the PostgreSQL
    database using environment variables."""
    return connect(
        dbname=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        cursor_factory=RealDictCursor
    )


def get_regular_client(config: dict):
    return OpenAI(
        api_key=config["OPENAI_API_KEY"]
    )


def get_match_data(config: dict, match_id: int) -> dict[str]:
    """Get match data from database."""

    match_query = """
    SELECT 
        m.match_id,
        m.match_date,
        ht.team_name as home_team,
        at.team_name as away_team,
        c.competition_name,
        s.season_name
    FROM match m
    JOIN team ht ON m.home_team_id = ht.team_id
    JOIN team at ON m.away_team_id = at.team_id
    JOIN match_assignment ma USING(match_id)
    JOIN competition c USING(competition_id)
    JOIN season s USING(season_id)
    WHERE m.match_id = %s
    """

    stats_query = """
    SELECT 
        mms.*
    FROM match_minute_stats mms
    WHERE mms.match_id = %s
    ORDER BY mms.match_minute, mms.half
    """

    events_query = """
    SELECT 
        me.match_event_id,
        mms.match_minute,
        mms.half,
        et.type_name as event_type,
        t.team_name,
        p.player_name
        FROM match_event me
    JOIN match_minute_stats mms USING(match_minute_stats_id)
    JOIN event_type et USING(event_type_id)
    JOIN team t USING(team_id)
    JOIN player_match_event pme USING(match_event_id)
    JOIN player p USING(player_id)
    WHERE mms.match_id = %s
    ORDER BY mms.match_minute, mms.half, me.match_event_id
    """

    conn = get_db_connection(config)
    with conn.cursor() as cur:
        cur.execute(match_query, (match_id,))
        match_info = cur.fetchone()

        if not match_info:
            raise ValueError(f"Match with ID {match_id} not found")

        cur.execute(stats_query, (match_id,))
        match_stats = cur.fetchall()

        cur.execute(events_query, (match_id,))
        match_events = cur.fetchall()
    return {
        'match_info': dict(match_info),
        'match_stats': [dict(stat) for stat in match_stats],
        'match_events': [dict(event) for event in match_events]
    }


def generate_match_report(config: dict, client: OpenAI, match_id: int) -> MatchReport:
    """Generate AI-powered match report"""

    match_data = get_match_data(config, match_id)
    match_info = match_data['match_info']

    stats_data = pd.DataFrame(match_data['match_stats'])
    events_data = pd.DataFrame(match_data['match_events'])

    prompt = create_match_analysis_prompt(
        match_info, stats_data, events_data)
    chat_completion = client.beta.chat.completions.parse(
        messages=[
            {"role": "system", "content": "You are an expert football commentator and analyst. Generate engaging match reports with insightful commentary using only the stats provided."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        model="gpt-4.1-nano",
        response_format=MatchReport,
    )

    try:
        return MatchReport.model_validate(json.loads(chat_completion.choices[0].message.content))
    except (TypeError, json.JSONDecodeError):
        return MatchReport.model_validate(json.loads(chat_completion.choices[0].message.refusal))


def create_match_analysis_prompt(match_info: dict, stats_data: pd.DataFrame, events_data: pd.DataFrame) -> str:
    """Create detailed prompt for AI analysis"""

    final_stats = stats_data.iloc[-1] if not stats_data.empty else {}
    total_shots_home = final_stats.get('shots_home', 0)
    total_shots_away = final_stats.get('shots_away', 0)
    final_possession_home = final_stats.get('possession_home', 50)

    significant_events = events_data[events_data['event_type'].isin(
        ['goal', 'redcard', 'tellowcard', 'substitution'])].to_dict('records')

    prompt = f"""
    You must analyse this football match and create a comprehensive report using only the data below.:

    MATCH DETAILS:
    - Home Team: {match_info['home_team']}
    - Away Team: {match_info['away_team']}
    - Date: {match_info['match_date']}
    - Competition: {match_info['competition_name']}
    - Season: {match_info['season_name']}

    HOME STATISTICS:
    - Total Shots: {match_info['home_team']} {total_shots_home} 
    - Final Possession: {match_info['home_team']} {final_possession_home}%

    AWAY STATISTICS:
    - Total Shots: {match_info['away_team']} {total_shots_away} 
    - Final Possession: {match_info['away_team']} {100-final_possession_home}%

    MINUTE-BY-MINUTE STATS:
    {stats_data.to_string() if not stats_data.empty else "No detailed stats available"}

    KEY MATCH EVENTS:
    {significant_events}

    1. An engaging match title
    2. Final score - count the number of "goal" events for each team.
    3. Overall match summary
    4. Period-by-period analysis (First Half, Second Half, etc.)
    5. Commentary on key events with specific player and team references
    6. Final thoughts on the match

    You must be:
    - Engaging and professional, similar tone to British football commentary
    - References specific players and teams
    - Mentions tactical aspects when relevant
    - Highlights turning points in the match
    - Uses football terminology appropriately

    DO NOT MAKE UP ANYTHING.
    DO NOT HALLUCINATE.

    """
    return prompt


def html_to_pdf(html_content: str, output_path: str) -> bool:
    """Convert HTML to PDF using xhtml2pdf"""
    try:
        with open(output_path, "wb") as result_file:
            pdf = pisa.CreatePDF(html_content, dest=result_file)
        return not pdf.err
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False


def create_email_message(pdf_path: str, match_title: str,
                         sender_email: str, recipient_email: str) -> MIMEMultipart:
    """Create email message with PDF attachment"""

    msg = MIMEMultipart('mixed')
    msg['Subject'] = f"Match Report: {match_title}"
    msg['From'] = sender_email
    msg['To'] = recipient_email

    msg_body = MIMEMultipart('alternative')
    body_text = f"""
    Dear Football Fan,
    
    Please find attached the detailed match report for: {match_title}
    
    This comprehensive report includes:
    - Complete match analysis
    - Period-by-period breakdown
    - Key events and player performances
    - Expert commentary and insights
    
    Best regards,
    PlayByPlay Insights Team
    """

    textpart = MIMEText(body_text, 'plain')
    msg_body.attach(textpart)
    msg.attach(msg_body)

    with open(pdf_path, 'rb') as f:
        part = MIMEApplication(f.read())
        part.add_header('Content-Disposition', 'attachment',
                        filename=basename(pdf_path))
        msg.attach(part)

    return msg


def generate_report(report: MatchReport) -> str:
    """Generate HTML version of the match report"""

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{report.match_title}</title>
        <style>            
            body {{
        font-family: 'Inter', sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #1e1d1d;
                color: #c8c8c8;
            }}
            
            .container {{
        max-width: 800px;
                margin: 0 auto;
                background: #2a2929;
                border-radius: 12px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            
            .header {{
        background: linear-gradient(135deg, #953e3b 0%, #671512 100%);
                color: c8c8c8;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
        margin: 0 0 10px 0;
                font-size: 2.2em;
                font-weight: 700;
            }}
            
            .match-info {{
        display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 15px;
                font-size: 1.1em;
            }}
            
            .score {{
        font-size: 2.5em;
                font-weight: 700;
                margin: 20px 0;
            }}
            
            .content {{
        padding: 30px;
            }}
            
            .section {{
        margin-bottom: 30px;
            }}
            
            .section h2 {{
        color: #953e3b;
                border-bottom: 3px solid #363636;
                padding-bottom: 8px;
                margin-bottom: 20px;
                font-size: 1.4em;
                font-weight: 600;
            }}
            
            .period-summary {{
        background: #363636;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 15px;
                border-left: 4px solid #2a9336;
            }}
            
            .period-summary h3 {{
        margin-top: 0;
                color: #953e3b;
                font-weight: 600;
            }}
            
            .event {{
        background: #363636;
                border: 1px solid #363636;
                border-radius: 6px;
                padding: 15px;
                margin-bottom: 10px;
                transition: box-shadow 0.2s;
            }}
            
            .event:hover {{
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            
            .event-header {{
        display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }}
            
            .event-time {{
        background: #2a9336;
                color: #c8c8c8;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 600;
            }}
            
            .event-type {{
        background: #2a9336;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: 500;
            }}
            
            .team-name {{
        font-weight: 600;
                color: #c8c8c8;
            }}
            
            .player-name {{
        font-weight: 500;
                color: #c8c8c8;
            }}
            
            .footer {{
        background: #1e1d1d;
                padding: 20px 30px;
                border-top: 1px solid #363636;
                text-align: center;
                color: #8b6464;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{report.match_title}</h1>
                <div class="score">{report.final_score}</div>
                <div class="match-info">
                    <span>{report.match_date}</span>
                    <span>{report.competition} - {report.season}</span>
                </div>
            </div>
            
            <div class="content">
                <div class="section">
                    <h2>Match Summary</h2>
                    <p>{report.match_summary}</p>
                </div>
                
                <div class="section">
                    <h2>Period Analysis</h2>
                    {"".join([f'''
                    <div class="period-summary">
                        <h3>{period.period}</h3>
                        <p><strong>Key Stats:</strong> {period.key_stats}</p>
                        <p>{period.commentary}</p>
                    </div>
                    ''' for period in report.period_summaries])}
                </div>
                
                <div class="section">
                    <h2>Key Events</h2>
                    {"".join([f'''
                    <div class="event">
                        <div class="event-header">
                            <span class="event-time">{event.minute}' H{event.half}</span>
                            <span class="event-type">{event.event_type.capitalize()}</span>
                        </div>
                        <p>
                            <span class="team-name">{event.team_name}</span>
                            {f' - <span class="player-name">{event.player_name}</span>' if event.player_name else ''}
                            {f' ({event.related_player_name})' if event.related_player_name else ''}
                        </p>
                        <p>{event.commentary}</p>
                    </div>
                    ''' for event in report.key_events])}
                </div>
                
                <div class="section">
                    <h2>Final Thoughts</h2>
                    <p>{report.final_thoughts}</p>
                </div>
            </div>
            
            <div class="footer">
                <p>Match Report Generated by Chat GPT 4.1 Nano on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_template


def generate_complete_report(config: dict, match_id: int, output_dir: str = "reports",
                             sender_email: str = None, recipient_email: str = None) -> dict[str, str]:
    """Generate complete match report with HTML, PDF, and email"""

    makedirs(output_dir, exist_ok=True)

    print(f"Generating AI analysis for match {match_id}...")
    client = get_regular_client(config)
    report = generate_match_report(config, client, match_id)

    print("Creating HTML report...")
    html_content = generate_report(report)

    html_filename = f"match_{match_id}_report.html"
    html_path = join(output_dir, html_filename)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Converting to PDF...")
    pdf_filename = f"match_{match_id}_report.pdf"
    pdf_path = join(output_dir, pdf_filename)
    pdf_success = html_to_pdf(html_content, pdf_path)

    results = {
        'html_path': html_path,
        'pdf_path': pdf_path if pdf_success else None,
        'report_data': report.model_dump()
    }

    if sender_email and recipient_email and pdf_success:
        print("Creating email message...")
        email_msg = create_email_message(
            pdf_path, report.match_title, sender_email, recipient_email
        )
        results['email_message'] = email_msg.as_string()

    print(f"Report generation complete! Files saved to {output_dir}")
    return results


def lambda_handler(event, context) -> None:
    """
    AWS Lambda handler function.

    Args:
        event: Lambda event data
        context: Lambda context object

    Returns:
        Dictionary with status code and response body
    """


if __name__ == "__main__":
    load_dotenv()

    match_id = 19367880

    generate_complete_report(
        ENV,
        match_id,
        output_dir="reports",
        sender_email="trainee.ahmet.cengiz@sigmalabs.co.uk",
        recipient_email="trainee.ahmet.cengiz@sigmalabs.co.uk"
    )
