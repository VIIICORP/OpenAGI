"""
Defense and Central Intelligence Administration Module for OpenAGI
Educational simulation of security and intelligence operations
"""

import hashlib
import threading
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set
from dataclasses import dataclass
from enum import Enum
from core import BaseModule, SystemStatus, Priority


class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = 1
    MODERATE = 2
    ELEVATED = 3
    HIGH = 4
    CRITICAL = 5


class SecurityEventType(Enum):
    """Types of security events"""
    INTRUSION_ATTEMPT = "intrusion_attempt"
    MALWARE_DETECTED = "malware_detected"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_BREACH = "data_breach"
    DDOS_ATTACK = "ddos_attack"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_VULNERABILITY = "system_vulnerability"


@dataclass
class SecurityEvent:
    """Security event record"""
    id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    source_ip: str
    target: str
    description: str
    timestamp: datetime
    mitigation_status: str = "pending"
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class IntelligenceReport:
    """Intelligence report structure"""
    id: str
    classification: str
    source: str
    subject: str
    content: str
    created_at: datetime
    expiry_date: datetime
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class DefenseIntelligenceModule(BaseModule):
    """Defense and Central Intelligence Administration"""
    
    def __init__(self):
        super().__init__("DefenseIntelligence")
        self.current_threat_level = ThreatLevel.LOW
        self.security_events: List[SecurityEvent] = []
        self.intelligence_reports: Dict[str, IntelligenceReport] = {}
        self.blocked_ips: Set[str] = set()
        self.monitored_entities: Dict[str, Dict[str, Any]] = {}
        self.detection_rules: List[Dict[str, Any]] = []
        self.alert_subscribers: List[callable] = []
        
        # Initialize detection rules
        self._initialize_detection_rules()
        
    def initialize(self) -> bool:
        """Initialize the defense and intelligence module"""
        try:
            self.logger.info("Initializing Defense and Intelligence module...")
            self._load_threat_intelligence()
            self.status = SystemStatus.RUNNING
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Defense Intelligence: {e}")
            self.status = SystemStatus.ERROR
            return False
            
    def start(self) -> bool:
        """Start defense and intelligence operations"""
        try:
            self._running = True
            self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._thread.start()
            
            self.logger.info("Defense and Intelligence operations started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Defense Intelligence: {e}")
            return False
            
    def stop(self) -> bool:
        """Stop defense and intelligence operations"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.status = SystemStatus.SHUTDOWN
        self.logger.info("Defense and Intelligence operations stopped")
        return True
        
    def _initialize_detection_rules(self):
        """Initialize security detection rules"""
        self.detection_rules = [
            {
                'name': 'Brute Force Detection',
                'description': 'Detect multiple failed login attempts',
                'threshold': 5,
                'timeframe': 300,  # 5 minutes
                'severity': ThreatLevel.ELEVATED
            },
            {
                'name': 'Unusual Traffic Pattern',
                'description': 'Detect abnormal network traffic',
                'threshold': 1000,  # requests per minute
                'timeframe': 60,
                'severity': ThreatLevel.MODERATE
            },
            {
                'name': 'Privilege Escalation',
                'description': 'Detect unauthorized privilege escalation',
                'threshold': 1,
                'timeframe': 0,
                'severity': ThreatLevel.HIGH
            }
        ]
        
    def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        # Simulate loading threat intelligence
        known_threats = [
            "192.168.1.100",  # Known malicious IP
            "10.0.0.50",      # Suspicious IP
            "203.0.113.45"    # Blocked IP
        ]
        
        for ip in known_threats:
            self.blocked_ips.add(ip)
            
        self.logger.info(f"Loaded {len(known_threats)} known threat indicators")
        
    def _monitoring_loop(self):
        """Main monitoring and detection loop"""
        while self._running:
            try:
                self._simulate_security_monitoring()
                self._update_threat_level()
                self._cleanup_old_events()
                self.heartbeat()
                time.sleep(10)  # Monitor every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)
                
    def _simulate_security_monitoring(self):
        """Simulate security monitoring activities"""
        # Randomly generate security events for demonstration
        if random.random() < 0.1:  # 10% chance per cycle
            event_type = random.choice(list(SecurityEventType))
            threat_level = random.choice(list(ThreatLevel))
            
            # Generate a realistic IP address
            source_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            
            self._create_security_event(
                event_type=event_type,
                threat_level=threat_level,
                source_ip=source_ip,
                target="system",
                description=f"Simulated {event_type.value} from {source_ip}"
            )
            
    def _create_security_event(self, event_type: SecurityEventType, threat_level: ThreatLevel,
                              source_ip: str, target: str, description: str, details: Dict[str, Any] = None):
        """Create a new security event"""
        event_id = hashlib.md5(f"{datetime.now().isoformat()}{source_ip}{event_type.value}".encode()).hexdigest()[:16]
        
        event = SecurityEvent(
            id=event_id,
            event_type=event_type,
            threat_level=threat_level,
            source_ip=source_ip,
            target=target,
            description=description,
            timestamp=datetime.now(),
            details=details or {}
        )
        
        self.security_events.append(event)
        
        # Auto-mitigate based on threat level
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._auto_mitigate(event)
            
        # Notify subscribers
        self._notify_security_alert(event)
        
        self.logger.warning(f"Security Event {event_id}: {description} (Threat Level: {threat_level.name})")
        
    def _auto_mitigate(self, event: SecurityEvent):
        """Automatically mitigate high-priority threats"""
        try:
            if event.event_type in [SecurityEventType.INTRUSION_ATTEMPT, SecurityEventType.DDOS_ATTACK]:
                self.blocked_ips.add(event.source_ip)
                event.mitigation_status = "ip_blocked"
                self.logger.info(f"Auto-blocked IP {event.source_ip} due to {event.event_type.value}")
                
            elif event.event_type == SecurityEventType.MALWARE_DETECTED:
                event.mitigation_status = "quarantined"
                self.logger.info(f"Auto-quarantined threat from {event.source_ip}")
                
            elif event.event_type == SecurityEventType.UNAUTHORIZED_ACCESS:
                event.mitigation_status = "access_revoked"
                self.logger.info(f"Auto-revoked access for {event.source_ip}")
                
        except Exception as e:
            self.logger.error(f"Error in auto-mitigation: {e}")
            event.mitigation_status = "mitigation_failed"
            
    def _update_threat_level(self):
        """Update overall system threat level"""
        recent_events = [e for e in self.security_events 
                        if (datetime.now() - e.timestamp).total_seconds() < 3600]  # Last hour
        
        if not recent_events:
            new_level = ThreatLevel.LOW
        else:
            # Calculate threat level based on recent events
            max_threat = max(event.threat_level for event in recent_events)
            critical_count = sum(1 for e in recent_events if e.threat_level == ThreatLevel.CRITICAL)
            high_count = sum(1 for e in recent_events if e.threat_level == ThreatLevel.HIGH)
            
            if critical_count > 0:
                new_level = ThreatLevel.CRITICAL
            elif high_count > 2:
                new_level = ThreatLevel.HIGH
            elif high_count > 0:
                new_level = ThreatLevel.ELEVATED
            else:
                new_level = max_threat
                
        if new_level != self.current_threat_level:
            old_level = self.current_threat_level
            self.current_threat_level = new_level
            self.logger.info(f"Threat level changed from {old_level.name} to {new_level.name}")
            
    def _cleanup_old_events(self):
        """Clean up old security events"""
        cutoff_time = datetime.now() - timedelta(days=7)
        original_count = len(self.security_events)
        self.security_events = [e for e in self.security_events if e.timestamp > cutoff_time]
        cleaned_count = original_count - len(self.security_events)
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old security events")
            
    def _notify_security_alert(self, event: SecurityEvent):
        """Notify subscribers of security alerts"""
        for subscriber in self.alert_subscribers:
            try:
                subscriber(event)
            except Exception as e:
                self.logger.error(f"Error notifying alert subscriber: {e}")
                
    def create_intelligence_report(self, classification: str, source: str, subject: str, 
                                 content: str, expiry_days: int = 30, tags: List[str] = None) -> str:
        """Create a new intelligence report"""
        report_id = hashlib.md5(f"{datetime.now().isoformat()}{subject}".encode()).hexdigest()[:16]
        
        report = IntelligenceReport(
            id=report_id,
            classification=classification,
            source=source,
            subject=subject,
            content=content,
            created_at=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=expiry_days),
            tags=tags or []
        )
        
        self.intelligence_reports[report_id] = report
        self.logger.info(f"Created intelligence report {report_id}: {subject}")
        return report_id
        
    def block_ip(self, ip_address: str, reason: str = "Manual block"):
        """Block an IP address"""
        self.blocked_ips.add(ip_address)
        self.logger.info(f"Blocked IP {ip_address}: {reason}")
        
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            self.logger.info(f"Unblocked IP {ip_address}")
        else:
            self.logger.warning(f"IP {ip_address} was not blocked")
            
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if an IP address is blocked"""
        return ip_address in self.blocked_ips
        
    def get_status(self) -> Dict[str, Any]:
        """Get defense and intelligence module status"""
        recent_events = [e for e in self.security_events 
                        if (datetime.now() - e.timestamp).total_seconds() < 3600]
        
        event_summary = {}
        for event_type in SecurityEventType:
            event_summary[event_type.value] = sum(1 for e in recent_events 
                                                 if e.event_type == event_type)
            
        return {
            'module': self.name,
            'status': self.status.value,
            'current_threat_level': self.current_threat_level.name,
            'total_security_events': len(self.security_events),
            'recent_events_1h': len(recent_events),
            'event_summary': event_summary,
            'blocked_ips_count': len(self.blocked_ips),
            'intelligence_reports': len(self.intelligence_reports),
            'monitored_entities': len(self.monitored_entities),
            'uptime': (datetime.now() - self.created_at).total_seconds()
        }
        
    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent security events"""
        recent_events = sorted(self.security_events, 
                             key=lambda e: e.timestamp, reverse=True)[:limit]
        
        return [
            {
                'id': event.id,
                'type': event.event_type.value,
                'threat_level': event.threat_level.name,
                'source_ip': event.source_ip,
                'target': event.target,
                'description': event.description,
                'timestamp': event.timestamp.isoformat(),
                'mitigation_status': event.mitigation_status
            }
            for event in recent_events
        ]
        
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IP addresses"""
        return list(self.blocked_ips)
        
    def subscribe_to_alerts(self, callback: callable):
        """Subscribe to security alerts"""
        self.alert_subscribers.append(callback)
        
    def search_intelligence_reports(self, query: str, classification: str = None) -> List[Dict[str, Any]]:
        """Search intelligence reports"""
        results = []
        query_lower = query.lower()
        
        for report in self.intelligence_reports.values():
            if classification and report.classification != classification:
                continue
                
            if (query_lower in report.subject.lower() or 
                query_lower in report.content.lower() or
                any(query_lower in tag.lower() for tag in report.tags)):
                
                results.append({
                    'id': report.id,
                    'classification': report.classification,
                    'source': report.source,
                    'subject': report.subject,
                    'created_at': report.created_at.isoformat(),
                    'tags': report.tags
                })
                
        return results