"""
Government Operations Module for OpenAGI
Simulates governmental administrative functions for educational purposes
"""

import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from core import BaseModule, SystemStatus, Priority


class DocumentStatus(Enum):
    """Document processing status"""
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING_SIGNATURE = "pending_signature"
    COMPLETED = "completed"


class ServiceType(Enum):
    """Types of government services"""
    PERMIT = "permit"
    LICENSE = "license"
    REGISTRATION = "registration"
    CERTIFICATION = "certification"
    INQUIRY = "inquiry"
    COMPLAINT = "complaint"


@dataclass
class Document:
    """Government document record"""
    id: str
    title: str
    document_type: str
    content: str
    status: DocumentStatus
    priority: Priority
    submitted_by: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    deadline: Optional[datetime] = None
    
    
@dataclass
class Citizen:
    """Citizen record"""
    id: str
    name: str
    email: str
    phone: str
    address: str
    registration_date: datetime
    services_used: List[str]
    
    def __post_init__(self):
        if not self.services_used:
            self.services_used = []


@dataclass
class ServiceRequest:
    """Government service request"""
    id: str
    citizen_id: str
    service_type: ServiceType
    description: str
    status: DocumentStatus
    priority: Priority
    created_at: datetime
    processing_time_hours: int
    assigned_department: str
    fee_amount: float = 0.0


class GovernmentOperationsModule(BaseModule):
    """Government operations and citizen services"""
    
    def __init__(self):
        super().__init__("GovernmentOperations")
        self.documents: Dict[str, Document] = {}
        self.citizens: Dict[str, Citizen] = {}
        self.service_requests: Dict[str, ServiceRequest] = {}
        self.departments = {
            'administration': 'General Administration',
            'licensing': 'Licensing Department',
            'permits': 'Permits and Planning',
            'registration': 'Registration Services',
            'complaints': 'Citizen Complaints'
        }
        self.processing_queue: List[str] = []
        self.statistics = {
            'total_requests': 0,
            'completed_requests': 0,
            'average_processing_time': 0.0
        }
        
    def initialize(self) -> bool:
        """Initialize government operations"""
        try:
            self.logger.info("Initializing Government Operations module...")
            self._initialize_sample_data()
            self.status = SystemStatus.RUNNING
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Government Operations: {e}")
            self.status = SystemStatus.ERROR
            return False
            
    def start(self) -> bool:
        """Start government services"""
        try:
            self._running = True
            self._thread = threading.Thread(target=self._processing_loop, daemon=True)
            self._thread.start()
            
            self.logger.info("Government Operations services started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Government Operations: {e}")
            return False
            
    def stop(self) -> bool:
        """Stop government services"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.status = SystemStatus.SHUTDOWN
        self.logger.info("Government Operations services stopped")
        return True
        
    def _initialize_sample_data(self):
        """Initialize with sample government data"""
        # Sample citizens
        sample_citizens = [
            {
                'id': 'citizen001',
                'name': 'John Public',
                'email': 'john.public@email.com',
                'phone': '555-0101',
                'address': '123 Main St, Anytown'
            },
            {
                'id': 'citizen002',
                'name': 'Jane Citizen',
                'email': 'jane.citizen@email.com',
                'phone': '555-0102',
                'address': '456 Oak Ave, Somewhere'
            }
        ]
        
        for citizen_data in sample_citizens:
            citizen = Citizen(
                id=citizen_data['id'],
                name=citizen_data['name'],
                email=citizen_data['email'],
                phone=citizen_data['phone'],
                address=citizen_data['address'],
                registration_date=datetime.now(),
                services_used=[]
            )
            self.citizens[citizen.id] = citizen
            
        self.logger.info(f"Initialized with {len(self.citizens)} citizen records")
        
    def _processing_loop(self):
        """Main processing loop for government services"""
        while self._running:
            try:
                self._process_pending_requests()
                self._update_statistics()
                self.heartbeat()
                time.sleep(60)  # Process every minute
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(10)
                
    def _process_pending_requests(self):
        """Process pending service requests"""
        for request_id in list(self.processing_queue):
            if request_id in self.service_requests:
                request = self.service_requests[request_id]
                
                # Simulate processing time
                time_elapsed = (datetime.now() - request.created_at).total_seconds() / 3600
                
                if time_elapsed >= request.processing_time_hours:
                    # Complete the request
                    request.status = DocumentStatus.COMPLETED
                    self.processing_queue.remove(request_id)
                    
                    self.logger.info(f"Completed service request {request_id}")
                    
                elif request.status == DocumentStatus.SUBMITTED:
                    # Move to under review
                    request.status = DocumentStatus.UNDER_REVIEW
                    
    def _update_statistics(self):
        """Update processing statistics"""
        total_requests = len(self.service_requests)
        completed_requests = sum(1 for r in self.service_requests.values() 
                               if r.status == DocumentStatus.COMPLETED)
        
        if completed_requests > 0:
            total_processing_time = sum(
                (datetime.now() - r.created_at).total_seconds() / 3600
                for r in self.service_requests.values()
                if r.status == DocumentStatus.COMPLETED
            )
            average_processing_time = total_processing_time / completed_requests
        else:
            average_processing_time = 0.0
            
        self.statistics = {
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'average_processing_time': average_processing_time
        }
        
    def register_citizen(self, name: str, email: str, phone: str, address: str) -> str:
        """Register a new citizen"""
        citizen_id = f"citizen{len(self.citizens):03d}"
        
        citizen = Citizen(
            id=citizen_id,
            name=name,
            email=email,
            phone=phone,
            address=address,
            registration_date=datetime.now(),
            services_used=[]
        )
        
        self.citizens[citizen_id] = citizen
        
        self.logger.info(f"Registered citizen {citizen_id}: {name}")
        return citizen_id
        
    def submit_service_request(self, citizen_id: str, service_type: ServiceType, 
                             description: str, priority: Priority = Priority.MEDIUM) -> str:
        """Submit a new service request"""
        if citizen_id not in self.citizens:
            raise ValueError(f"Citizen {citizen_id} not found")
            
        request_id = f"req_{len(self.service_requests):04d}"
        
        # Determine processing time and department based on service type
        processing_times = {
            ServiceType.PERMIT: 72,      # 3 days
            ServiceType.LICENSE: 48,     # 2 days
            ServiceType.REGISTRATION: 24, # 1 day
            ServiceType.CERTIFICATION: 96, # 4 days
            ServiceType.INQUIRY: 4,      # 4 hours
            ServiceType.COMPLAINT: 8     # 8 hours
        }
        
        department_mapping = {
            ServiceType.PERMIT: 'permits',
            ServiceType.LICENSE: 'licensing',
            ServiceType.REGISTRATION: 'registration',
            ServiceType.CERTIFICATION: 'licensing',
            ServiceType.INQUIRY: 'administration',
            ServiceType.COMPLAINT: 'complaints'
        }
        
        request = ServiceRequest(
            id=request_id,
            citizen_id=citizen_id,
            service_type=service_type,
            description=description,
            status=DocumentStatus.SUBMITTED,
            priority=priority,
            created_at=datetime.now(),
            processing_time_hours=processing_times[service_type],
            assigned_department=department_mapping[service_type],
            fee_amount=self._calculate_service_fee(service_type)
        )
        
        self.service_requests[request_id] = request
        self.processing_queue.append(request_id)
        
        # Update citizen record
        citizen = self.citizens[citizen_id]
        citizen.services_used.append(request_id)
        
        self.logger.info(f"Submitted service request {request_id} for citizen {citizen_id}")
        return request_id
        
    def _calculate_service_fee(self, service_type: ServiceType) -> float:
        """Calculate fee for service type"""
        fee_schedule = {
            ServiceType.PERMIT: 150.00,
            ServiceType.LICENSE: 75.00,
            ServiceType.REGISTRATION: 25.00,
            ServiceType.CERTIFICATION: 100.00,
            ServiceType.INQUIRY: 0.00,
            ServiceType.COMPLAINT: 0.00
        }
        return fee_schedule.get(service_type, 0.00)
        
    def submit_document(self, title: str, document_type: str, content: str,
                       submitted_by: str, priority: Priority = Priority.MEDIUM,
                       deadline: Optional[datetime] = None) -> str:
        """Submit a government document"""
        document_id = f"doc_{len(self.documents):04d}"
        
        document = Document(
            id=document_id,
            title=title,
            document_type=document_type,
            content=content,
            status=DocumentStatus.SUBMITTED,
            priority=priority,
            submitted_by=submitted_by,
            assigned_to=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deadline=deadline
        )
        
        self.documents[document_id] = document
        
        self.logger.info(f"Submitted document {document_id}: {title}")
        return document_id
        
    def approve_document(self, document_id: str, approved_by: str) -> bool:
        """Approve a government document"""
        if document_id not in self.documents:
            return False
            
        document = self.documents[document_id]
        document.status = DocumentStatus.APPROVED
        document.assigned_to = approved_by
        document.updated_at = datetime.now()
        
        self.logger.info(f"Document {document_id} approved by {approved_by}")
        return True
        
    def reject_document(self, document_id: str, rejected_by: str, reason: str) -> bool:
        """Reject a government document"""
        if document_id not in self.documents:
            return False
            
        document = self.documents[document_id]
        document.status = DocumentStatus.REJECTED
        document.assigned_to = rejected_by
        document.updated_at = datetime.now()
        document.content += f"\n\nRejection Reason: {reason}"
        
        self.logger.info(f"Document {document_id} rejected by {rejected_by}")
        return True
        
    def get_citizen_services(self, citizen_id: str) -> List[Dict[str, Any]]:
        """Get all services used by a citizen"""
        if citizen_id not in self.citizens:
            return []
            
        citizen = self.citizens[citizen_id]
        services = []
        
        for request_id in citizen.services_used:
            if request_id in self.service_requests:
                request = self.service_requests[request_id]
                services.append({
                    'request_id': request.id,
                    'service_type': request.service_type.value,
                    'description': request.description,
                    'status': request.status.value,
                    'created_at': request.created_at.isoformat(),
                    'fee_amount': request.fee_amount,
                    'assigned_department': request.assigned_department
                })
                
        return services
        
    def get_department_workload(self, department: str) -> Dict[str, Any]:
        """Get workload statistics for a department"""
        if department not in self.departments:
            return {}
            
        dept_requests = [r for r in self.service_requests.values() 
                        if r.assigned_department == department]
        
        pending = sum(1 for r in dept_requests if r.status != DocumentStatus.COMPLETED)
        completed = sum(1 for r in dept_requests if r.status == DocumentStatus.COMPLETED)
        
        return {
            'department': department,
            'department_name': self.departments[department],
            'total_requests': len(dept_requests),
            'pending_requests': pending,
            'completed_requests': completed,
            'completion_rate': (completed / len(dept_requests) * 100) if dept_requests else 0
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Get government operations status"""
        pending_requests = sum(1 for r in self.service_requests.values() 
                             if r.status != DocumentStatus.COMPLETED)
        pending_documents = sum(1 for d in self.documents.values() 
                              if d.status == DocumentStatus.SUBMITTED)
        
        return {
            'module': self.name,
            'status': self.status.value,
            'total_citizens': len(self.citizens),
            'total_service_requests': len(self.service_requests),
            'pending_requests': pending_requests,
            'total_documents': len(self.documents),
            'pending_documents': pending_documents,
            'departments': len(self.departments),
            'statistics': self.statistics,
            'uptime': (datetime.now() - self.created_at).total_seconds()
        }
        
    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent government activity"""
        activities = []
        
        # Recent service requests
        recent_requests = sorted(self.service_requests.values(), 
                               key=lambda r: r.created_at, reverse=True)[:limit//2]
        
        for request in recent_requests:
            activities.append({
                'type': 'service_request',
                'id': request.id,
                'description': f"Service request: {request.service_type.value}",
                'status': request.status.value,
                'timestamp': request.created_at.isoformat()
            })
            
        # Recent documents
        recent_documents = sorted(self.documents.values(), 
                                key=lambda d: d.updated_at, reverse=True)[:limit//2]
        
        for document in recent_documents:
            activities.append({
                'type': 'document',
                'id': document.id,
                'description': f"Document: {document.title}",
                'status': document.status.value,
                'timestamp': document.updated_at.isoformat()
            })
            
        # Sort by timestamp
        activities.sort(key=lambda a: a['timestamp'], reverse=True)
        return activities[:limit]