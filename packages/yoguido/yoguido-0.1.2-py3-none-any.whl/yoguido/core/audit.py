"""
GXP-Compliant Audit Trail System for YoGuido
Add to: yoguido/core/audit.py

Implements FDA 21 CFR Part 11 and EU Annex 11 requirements:
- Complete user session tracking
- Data access/modification logging  
- Electronic signatures
- Tamper-evident logs
- User authentication trails
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
import threading
import queue
import logging
from cryptography.fernet import Fernet
import base64

@dataclass
class AuditEvent:
    """Single audit trail event - GXP compliant structure"""
    event_id: str
    session_id: str
    user_id: str
    user_name: str
    timestamp: str
    event_type: str
    event_category: str
    component_id: Optional[str]
    page_path: Optional[str]
    action: str
    data_before: Optional[Dict] = None
    data_after: Optional[Dict] = None
    ip_address: str = "127.0.0.1"
    user_agent: str = ""
    signature_required: bool = False
    signature_status: str = "not_required"  # not_required, pending, signed, rejected
    signature_hash: Optional[str] = None
    signature_timestamp: Optional[str] = None
    risk_level: str = "low"  # low, medium, high, critical
    compliance_flags: List[str] = None
    previous_hash: Optional[str] = None
    event_hash: Optional[str] = None

class GXPAuditLogger:
    """GXP-compliant audit trail logging system"""
    
    def __init__(self, log_directory: str = "./gxp_logs", encryption_key: Optional[bytes] = None):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True, parents=True)
        
        # Initialize encryption for sensitive data
        if encryption_key is None:
            encryption_key = Fernet.generate_key()
        self.cipher = Fernet(encryption_key)
        
        # Store encryption key securely (in production, use proper key management)
        key_file = self.log_directory / ".audit_key"
        if not key_file.exists():
            with open(key_file, 'wb') as f:
                f.write(encryption_key)
        
        # Session tracking
        self.active_sessions: Dict[str, Dict] = {}
        self.last_hash: Optional[str] = None
        
        # Async logging queue
        self.log_queue = queue.Queue()
        self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.log_thread.start()
        
        # Setup structured logging
        self._setup_logging()
        
        print("🔒 GXP Audit Trail System initialized")
        print(f"📁 Logs directory: {self.log_directory}")
        
    def _setup_logging(self):
        """Setup structured logging for audit trails"""
        log_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )
        
        # Main audit log
        audit_handler = logging.FileHandler(
            self.log_directory / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
        )
        audit_handler.setFormatter(log_formatter)
        
        self.audit_logger = logging.getLogger('yoguido.audit')
        self.audit_logger.setLevel(logging.INFO)
        self.audit_logger.addHandler(audit_handler)
        
        # Security events log
        security_handler = logging.FileHandler(
            self.log_directory / f"security_{datetime.now().strftime('%Y%m%d')}.log"
        )
        security_handler.setFormatter(log_formatter)
        
        self.security_logger = logging.getLogger('yoguido.security')
        self.security_logger.setLevel(logging.INFO)
        self.security_logger.addHandler(security_handler)
        
    def _log_worker(self):
        """Background worker for async log writing"""
        while True:
            try:
                event = self.log_queue.get(timeout=1)
                if event is None:  # Shutdown signal
                    break
                self._write_audit_event(event)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Audit log worker error: {e}")
    
    def _calculate_hash(self, event: AuditEvent) -> str:
        """Calculate tamper-evident hash for audit event"""
        # Create deterministic string from event data
        event_data = {
            'event_id': event.event_id,
            'session_id': event.session_id,
            'user_id': event.user_id,
            'timestamp': event.timestamp,
            'event_type': event.event_type,
            'action': event.action,
            'data_before': event.data_before,
            'data_after': event.data_after,
            'previous_hash': event.previous_hash
        }
        
        event_string = json.dumps(event_data, sort_keys=True, default=str)
        return hashlib.sha256(event_string.encode()).hexdigest()
    
    def _encrypt_sensitive_data(self, data: Any) -> str:
        """Encrypt sensitive data in audit logs"""
        if data is None:
            return None
        
        data_string = json.dumps(data, default=str)
        encrypted = self.cipher.encrypt(data_string.encode())
        return base64.b64encode(encrypted).decode()
    
    def _write_audit_event(self, event: AuditEvent):
        """Write audit event to log files"""
        try:
            # Calculate hash for tamper evidence
            event.previous_hash = self.last_hash
            event.event_hash = self._calculate_hash(event)
            self.last_hash = event.event_hash
            
            # Encrypt sensitive data
            if event.data_before:
                event.data_before = self._encrypt_sensitive_data(event.data_before)
            if event.data_after:
                event.data_after = self._encrypt_sensitive_data(event.data_after)
            
            # Write to appropriate log
            if event.event_category in ['authentication', 'authorization', 'security']:
                self.security_logger.info(json.dumps(asdict(event)))
            else:
                self.audit_logger.info(json.dumps(asdict(event)))
            
            # Write to daily audit file
            daily_file = self.log_directory / f"audit_trail_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(daily_file, 'a') as f:
                f.write(json.dumps(asdict(event)) + '\n')
                
        except Exception as e:
            print(f"❌ Failed to write audit event: {e}")
    
    def create_session(self, user_id: str, user_name: str, ip_address: str = "127.0.0.1", 
                      user_agent: str = "") -> str:
        """Create new user session with audit trail"""
        session_id = str(uuid.uuid4())
        
        session_info = {
            'session_id': session_id,
            'user_id': user_id,
            'user_name': user_name,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'ip_address': ip_address,
            'user_agent': user_agent,
            'page_visits': [],
            'actions_count': 0,
            'data_accessed': [],
            'signatures_required': []
        }
        
        self.active_sessions[session_id] = session_info
        
        # Log session creation
        self.log_event(
            session_id=session_id,
            user_id=user_id,
            user_name=user_name,
            event_type="session_start",
            event_category="authentication",
            action="user_login",
            ip_address=ip_address,
            user_agent=user_agent,
            risk_level="medium"
        )
        
        return session_id
    
    def end_session(self, session_id: str):
        """End user session with audit trail"""
        if session_id in self.active_sessions:
            session_info = self.active_sessions[session_id]
            
            # Calculate session duration
            start_time = datetime.fromisoformat(session_info['start_time'])
            duration = datetime.now(timezone.utc) - start_time
            
            self.log_event(
                session_id=session_id,
                user_id=session_info['user_id'],
                user_name=session_info['user_name'],
                event_type="session_end",
                event_category="authentication",
                action="user_logout",
                data_after={
                    'session_duration_seconds': duration.total_seconds(),
                    'pages_visited': len(session_info['page_visits']),
                    'actions_performed': session_info['actions_count']
                },
                ip_address=session_info['ip_address'],
                risk_level="low"
            )
            
            del self.active_sessions[session_id]
    
    def log_event(self, session_id: str, user_id: str, user_name: str,
                  event_type: str, event_category: str, action: str,
                  component_id: Optional[str] = None, page_path: Optional[str] = None,
                  data_before: Optional[Dict] = None, data_after: Optional[Dict] = None,
                  ip_address: str = "127.0.0.1", user_agent: str = "",
                  signature_required: bool = False, risk_level: str = "low",
                  compliance_flags: Optional[List[str]] = None):
        """Log audit event asynchronously"""
        
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=user_id,
            user_name=user_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            event_category=event_category,
            component_id=component_id,
            page_path=page_path,
            action=action,
            data_before=data_before,
            data_after=data_after,
            ip_address=ip_address,
            user_agent=user_agent,
            signature_required=signature_required,
            risk_level=risk_level,
            compliance_flags=compliance_flags or []
        )
        
        # Update session tracking
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session['actions_count'] += 1
            
            if page_path and page_path not in session['page_visits']:
                session['page_visits'].append(page_path)
                
            if data_before or data_after:
                session['data_accessed'].append({
                    'timestamp': event.timestamp,
                    'component': component_id,
                    'action': action
                })
        
        # Queue for async processing
        self.log_queue.put(event)
    
    def log_page_access(self, session_id: str, user_id: str, user_name: str, 
                       page_path: str, page_title: str):
        """Log page access"""
        self.log_event(
            session_id=session_id,
            user_id=user_id,
            user_name=user_name,
            event_type="page_access",
            event_category="navigation",
            action="page_view",
            page_path=page_path,
            data_after={'page_title': page_title},
            risk_level="low"
        )
    
    def log_component_interaction(self, session_id: str, user_id: str, user_name: str,
                                component_id: str, component_type: str, action: str,
                                data_before: Optional[Dict] = None, data_after: Optional[Dict] = None):
        """Log component interaction"""
        # Determine risk level based on component and action
        risk_level = "low"
        if component_type in ['button', 'form'] and action in ['submit', 'save', 'delete']:
            risk_level = "medium"
        if action in ['delete', 'export', 'admin_action']:
            risk_level = "high"
            
        self.log_event(
            session_id=session_id,
            user_id=user_id,
            user_name=user_name,
            event_type="component_interaction",
            event_category="user_action",
            action=action,
            component_id=component_id,
            data_before=data_before,
            data_after=data_after,
            risk_level=risk_level
        )
    
    def log_data_access(self, session_id: str, user_id: str, user_name: str,
                       data_type: str, data_id: str, action: str,
                       data_before: Optional[Dict] = None, data_after: Optional[Dict] = None):
        """Log data access/modification"""
        # Data access is always medium to high risk
        risk_level = "medium" if action == "read" else "high"
        
        compliance_flags = []
        if action in ['create', 'update', 'delete']:
            compliance_flags.append('data_integrity')
        if data_type in ['user_data', 'clinical_data', 'financial_data']:
            compliance_flags.append('sensitive_data')
            
        signature_required = action in ['delete', 'critical_update'] or 'clinical_data' in data_type
        
        self.log_event(
            session_id=session_id,
            user_id=user_id,
            user_name=user_name,
            event_type="data_access",
            event_category="data_operation",
            action=action,
            component_id=f"{data_type}:{data_id}",
            data_before=data_before,
            data_after=data_after,
            signature_required=signature_required,
            risk_level=risk_level,
            compliance_flags=compliance_flags
        )
    
    def log_electronic_signature(self, session_id: str, user_id: str, user_name: str,
                                document_id: str, signature_meaning: str, signature_hash: str):
        """Log electronic signature"""
        self.log_event(
            session_id=session_id,
            user_id=user_id,
            user_name=user_name,
            event_type="electronic_signature",
            event_category="compliance",
            action="document_signed",
            component_id=document_id,
            data_after={
                'signature_meaning': signature_meaning,
                'signature_hash': signature_hash,
                'signature_timestamp': datetime.now(timezone.utc).isoformat()
            },
            signature_required=False,  # This IS the signature
            risk_level="critical",
            compliance_flags=['electronic_signature', 'regulatory_compliance']
        )
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get session summary for compliance reporting"""
        if session_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[session_id]
        
        return {
            'session_id': session_id,
            'user_id': session['user_id'],
            'user_name': session['user_name'],
            'start_time': session['start_time'],
            'duration_minutes': (datetime.now(timezone.utc) - 
                               datetime.fromisoformat(session['start_time'])).total_seconds() / 60,
            'pages_visited': session['page_visits'],
            'actions_count': session['actions_count'],
            'data_access_count': len(session['data_accessed']),
            'signatures_required': len(session['signatures_required']),
            'ip_address': session['ip_address']
        }
    
    def generate_compliance_report(self, start_date: str, end_date: str, 
                                  user_id: Optional[str] = None) -> Dict:
        """Generate GXP compliance report"""
        # This would read from log files and generate compliance reports
        # Implementation would depend on specific compliance requirements
        return {
            'report_generated': datetime.now(timezone.utc).isoformat(),
            'period': f"{start_date} to {end_date}",
            'user_filter': user_id,
            'total_sessions': 0,  # Would be calculated from logs
            'total_actions': 0,   # Would be calculated from logs
            'security_events': 0, # Would be calculated from logs
            'compliance_violations': []  # Would be calculated from logs
        }

# Global audit logger instance
_audit_logger: Optional[GXPAuditLogger] = None

def get_audit_logger() -> GXPAuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = GXPAuditLogger()
    return _audit_logger

def initialize_gxp_audit(log_directory: str = "./gxp_logs", 
                        encryption_key: Optional[bytes] = None) -> GXPAuditLogger:
    """Initialize GXP audit system"""
    global _audit_logger
    _audit_logger = GXPAuditLogger(log_directory, encryption_key)
    return _audit_logger