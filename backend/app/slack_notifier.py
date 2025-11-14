"""
Slack integration for notifications via Incoming Webhook.

This module provides a reusable helper function to post JSON messages
to Slack when tickets are created or content gaps are detected.
"""

import logging
from typing import Dict, Optional, Any
import httpx
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_slack_notification(
    message: str,
    title: Optional[str] = None,
    color: str = "good",
    fields: Optional[list] = None,
    webhook_url: Optional[str] = None
) -> bool:
    """
    Send a notification to Slack via Incoming Webhook.
    
    This is a reusable helper that posts JSON payloads to the configured
    SLACK_WEBHOOK_URL. It handles errors gracefully and logs failures.
    
    Args:
        message: Main message text to send
        title: Optional title for the Slack message
        color: Color for the message border (good, warning, danger, or hex)
        fields: Optional list of field dicts with 'title' and 'value' keys
        webhook_url: Optional webhook URL (defaults to SLACK_WEBHOOK_URL from config)
        
    Returns:
        bool: True if notification was sent successfully, False otherwise
        
    Example:
        >>> send_slack_notification(
        ...     message="New ticket created",
        ...     title="Ticket Alert",
        ...     fields=[
        ...         {"title": "Priority", "value": "High", "short": True},
        ...         {"title": "Category", "value": "Technical Issue", "short": True}
        ...     ]
        ... )
    """
    # Get webhook URL from parameter or config
    webhook = webhook_url or settings.slack_webhook_url
    
    if not webhook:
        logger.debug("Slack webhook URL not configured - skipping notification")
        return False
    
    # Validate webhook URL format
    if not webhook.startswith("https://hooks.slack.com/services/"):
        logger.warning(f"Invalid Slack webhook URL format: {webhook[:50]}...")
        return False
    
    # Build Slack attachment payload
    attachment = {
        "color": color,
        "text": message
    }
    
    if title:
        attachment["title"] = title
    
    if fields:
        attachment["fields"] = fields
    
    # Build full payload
    payload = {
        "attachments": [attachment]
    }
    
    try:
        # Send POST request to Slack webhook
        response = httpx.post(
            webhook,
            json=payload,
            timeout=10.0
        )
        
        # Check response
        if response.status_code == 200:
            response_text = response.text.strip()
            if response_text == "ok":
                logger.info("Slack notification sent successfully")
                return True
            else:
                logger.warning(f"Slack webhook returned unexpected response: {response_text}")
                return False
        else:
            logger.error(
                f"Slack webhook returned status {response.status_code}: {response.text}"
            )
            return False
            
    except httpx.TimeoutException:
        logger.error("Timeout while sending Slack notification")
        return False
    except httpx.RequestError as e:
        logger.error(f"Error sending Slack notification: {str(e)}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error sending Slack notification: {str(e)}")
        return False


def notify_ticket_created(
    ticket_text: str,
    priority: str,
    category: str,
    file_name: Optional[str] = None,
    ticket_id: Optional[str] = None
) -> bool:
    """
    Send a Slack notification when a new ticket is created.
    
    Args:
        ticket_text: The ticket content (truncated if too long)
        priority: Ticket priority (High, Medium, Low)
        category: Ticket category
        file_name: Optional file name if ticket was uploaded
        ticket_id: Optional ticket ID from database
        
    Returns:
        bool: True if notification was sent successfully
    """
    # Truncate ticket text if too long
    max_text_length = 500
    display_text = ticket_text[:max_text_length]
    if len(ticket_text) > max_text_length:
        display_text += "..."
    
    # Determine color based on priority
    color_map = {
        "High": "danger",
        "Medium": "warning",
        "Low": "good"
    }
    color = color_map.get(priority, "good")
    
    # Build fields
    fields = [
        {
            "title": "Priority",
            "value": priority,
            "short": True
        },
        {
            "title": "Category",
            "value": category,
            "short": True
        }
    ]
    
    if file_name:
        fields.append({
            "title": "Source",
            "value": f"File: {file_name}",
            "short": True
        })
    
    if ticket_id:
        fields.append({
            "title": "Ticket ID",
            "value": ticket_id,
            "short": True
        })
    
    return send_slack_notification(
        message=display_text,
        title="🎫 New Support Ticket Created",
        color=color,
        fields=fields
    )


def notify_content_gap_detected(
    gap: Dict[str, Any],
    total_gaps: int = 1
) -> bool:
    """
    Send a Slack notification when a content gap is detected.
    
    Args:
        gap: Dictionary containing gap information with keys:
            - topic_name: Name of the topic with gap
            - percentage: Percentage representation
            - keywords: List of keywords
            - gap_severity: Severity level (high, medium)
        total_gaps: Total number of gaps detected
        
    Returns:
        bool: True if notification was sent successfully
    """
    # Determine color based on severity
    color = "danger" if gap.get("gap_severity") == "high" else "warning"
    
    # Build fields
    fields = [
        {
            "title": "Topic",
            "value": gap.get("topic_name", "Unknown"),
            "short": False
        },
        {
            "title": "Coverage",
            "value": f"{gap.get('percentage', 0)}%",
            "short": True
        },
        {
            "title": "Severity",
            "value": gap.get("gap_severity", "medium").title(),
            "short": True
        }
    ]
    
    # Add keywords if available
    keywords = gap.get("keywords", [])
    if keywords:
        fields.append({
            "title": "Keywords",
            "value": ", ".join(keywords[:5]),
            "short": False
        })
    
    # Build message
    message = (
        f"Content gap detected in topic: *{gap.get('topic_name', 'Unknown')}*\n"
        f"Only {gap.get('percentage', 0)}% coverage - consider adding more content."
    )
    
    title = f"📊 Content Gap Detected"
    if total_gaps > 1:
        title += f" ({total_gaps} gaps found)"
    
    return send_slack_notification(
        message=message,
        title=title,
        color=color,
        fields=fields
    )

