"""Generates the HTML for the match Report."""
from datetime import datetime

from report_commentary import MatchReport


def generate_html(report: MatchReport) -> str:
    """Generate HTML version of the match report."""

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
