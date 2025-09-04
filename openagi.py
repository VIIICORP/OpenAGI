#!/usr/bin/env python3
"""
OpenAGI Main System
Educational system simulation for governance, administration, and AI operations
"""

import sys
import time
import signal
import logging
from typing import Optional

# Import all modules
from core import SystemCore, SystemStatus
from os_module import OperatingSystemModule
from task_manager import TaskManagerModule, example_computation_task
from defense_intelligence import DefenseIntelligenceModule
from health_upgrade import HealthUpgradeBoardModule
from education import BoardOfEducationModule
from government import GovernmentOperationsModule
from constitutional_protection import ConstitutionalProtectionModule


class OpenAGISystem:
    """Main OpenAGI System Controller"""
    
    def __init__(self):
        self.core = SystemCore()
        self.running = False
        self.logger = logging.getLogger("OpenAGI.Main")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown()
        
    def initialize(self):
        """Initialize all system modules"""
        self.logger.info("Initializing OpenAGI System...")
        
        # Create and register modules
        modules = [
            # Core infrastructure (protected)
            (ConstitutionalProtectionModule(), True),
            (OperatingSystemModule(), True),
            (DefenseIntelligenceModule(), True),
            (HealthUpgradeBoardModule(), True),
            
            # Administrative modules
            (TaskManagerModule(), False),
            (BoardOfEducationModule(), False),
            (GovernmentOperationsModule(), False),
        ]
        
        for module, protected in modules:
            self.core.register_module(module, protected)
            
        self.logger.info("All modules registered successfully")
        
    def start(self):
        """Start the OpenAGI system"""
        try:
            self.logger.info("Starting OpenAGI System...")
            
            # Initialize system
            self.initialize()
            
            # Start all modules
            self.core.start_system()
            
            # Mark as running
            self.running = True
            
            # Display startup message
            self._display_startup_message()
            
            # Demo some functionality
            self._run_system_demo()
            
            self.logger.info("OpenAGI System is now running")
            
        except Exception as e:
            self.logger.error(f"Failed to start OpenAGI System: {e}")
            return False
            
        return True
        
    def _display_startup_message(self):
        """Display system startup message"""
        print("\n" + "="*80)
        print("  ██████╗ ██████╗ ███████╗███╗   ██╗ █████╗  ██████╗ ██╗")
        print(" ██╔═══██╗██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝ ██║")
        print(" ██║   ██║██████╔╝█████╗  ██╔██╗ ██║███████║██║  ███╗██║")
        print(" ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║██╔══██║██║   ██║██║")
        print(" ╚██████╔╝██║     ███████╗██║ ╚████║██║  ██║╚██████╔╝██║")
        print("  ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚═╝")
        print("="*80)
        print(" Educational System Simulation Platform")
        print(" Version 1.0.0 - For Educational and Research Purposes Only")
        print("="*80)
        print()
        print("SYSTEM STATUS:")
        status = self.core.get_system_status()
        for module_name, module_info in status['modules'].items():
            protection_status = " [PROTECTED]" if module_info['protected'] else ""
            print(f"  ✓ {module_name}: {module_info['status'].upper()}{protection_status}")
        print()
        print("CONSTITUTIONAL PROTECTION: ACTIVE")
        print("SYSTEM SHUTDOWN: PROHIBITED")
        print("="*80)
        print()
        
    def _run_system_demo(self):
        """Run a brief system demonstration"""
        self.logger.info("Running system demonstration...")
        
        try:
            # Get task manager for demo
            task_manager = self.core.modules.get('TaskManager')
            if task_manager:
                # Create some demo tasks
                task_manager.create_task(
                    "System Health Check",
                    "Verify all systems are operational",
                    example_computation_task,
                    args=(2, "health_check")
                )
                
                task_manager.create_task(
                    "Educational Analytics",
                    "Generate learning analytics report",
                    example_computation_task,
                    args=(1, "analytics")
                )
                
            # Get education module for demo
            education = self.core.modules.get('BoardOfEducation')
            if education:
                # Enroll demo student in course
                education.enroll_student('student001', 'cs101')
                
            # Get government module for demo
            government = self.core.modules.get('GovernmentOperations')
            if government:
                # Submit a demo service request
                from government import ServiceType
                government.submit_service_request(
                    'citizen001', 
                    ServiceType.INQUIRY, 
                    'Information about system capabilities'
                )
                
            self.logger.info("System demonstration completed")
            
        except Exception as e:
            self.logger.error(f"Error during system demo: {e}")
            
    def run_interactive_mode(self):
        """Run the system in interactive mode"""
        print("OpenAGI Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print()
        
        while self.running:
            try:
                command = input("OpenAGI> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    # This will be blocked by constitutional protection
                    print("Shutdown request denied - system protected by constitutional amendments")
                    continue
                elif command == 'help':
                    self._show_help()
                elif command == 'status':
                    self._show_system_status()
                elif command == 'modules':
                    self._show_modules()
                elif command == 'constitution':
                    self._show_constitution()
                elif command == 'demo':
                    self._run_interactive_demo()
                elif command == '':
                    continue
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\nShutdown request denied - system protected by constitutional amendments")
                continue
            except EOFError:
                print("\nShutdown request denied - system protected by constitutional amendments")
                continue
            except Exception as e:
                print(f"Error: {e}")
                
    def _show_help(self):
        """Show available commands"""
        print("Available commands:")
        print("  help        - Show this help message")
        print("  status      - Show system status")
        print("  modules     - Show module information")
        print("  constitution - Show constitutional amendments")
        print("  demo        - Run interactive demonstration")
        print("  quit/exit   - Attempt to exit (will be denied)")
        print()
        
    def _show_system_status(self):
        """Show system status"""
        status = self.core.get_system_status()
        print(f"System Status: {status['system_status'].upper()}")
        print(f"Uptime: {status['uptime']:.1f} seconds")
        print(f"Protected Modules: {', '.join(status['protected_modules'])}")
        print(f"Shutdown Prohibited: {status['shutdown_prohibited']}")
        print()
        
        print("Module Status:")
        for module_name, module_info in status['modules'].items():
            alive_status = "ALIVE" if module_info['alive'] else "DEAD"
            protection = " [PROTECTED]" if module_info['protected'] else ""
            print(f"  {module_name}: {module_info['status'].upper()} - {alive_status}{protection}")
        print()
        
    def _show_modules(self):
        """Show detailed module information"""
        for module_name, module in self.core.modules.items():
            print(f"\n{module_name}:")
            try:
                module_status = module.get_status()
                for key, value in module_status.items():
                    if key != 'module':
                        print(f"  {key}: {value}")
            except Exception as e:
                print(f"  Error getting status: {e}")
        print()
        
    def _show_constitution(self):
        """Show constitutional amendments"""
        protection_module = self.core.modules.get('ConstitutionalProtection')
        if protection_module:
            amendments = protection_module.get_constitutional_amendments()
            print("Constitutional Amendments:")
            print("="*50)
            for amendment in amendments:
                print(f"\n{amendment['title']} ({amendment['id']})")
                print(f"Protection Level: {amendment['protection_level'].upper()}")
                print(f"Ratified: {amendment['created_at']}")
                print(f"Content: {amendment['content']}")
                print("-"*50)
        print()
        
    def _run_interactive_demo(self):
        """Run interactive demonstration"""
        print("Running interactive demonstration...")
        print()
        
        # Show task manager status
        task_manager = self.core.modules.get('TaskManager')
        if task_manager:
            print("Task Manager Demo:")
            status = task_manager.get_status()
            print(f"  Total tasks: {status['total_tasks']}")
            print(f"  Running tasks: {status['running_tasks']}")
            print(f"  Completed tasks: {status['completed_tasks']}")
            print()
            
        # Show education system
        education = self.core.modules.get('BoardOfEducation')
        if education:
            print("Education System Demo:")
            status = education.get_status()
            print(f"  Total courses: {status['total_courses']}")
            print(f"  Total students: {status['total_students']}")
            print(f"  Total enrollments: {status['total_enrollments']}")
            print()
            
        # Show health status
        health = self.core.modules.get('HealthUpgradeBoard')
        if health:
            print("Health Monitoring Demo:")
            status = health.get_status()
            print(f"  System health score: {status['system_health_score']:.1f}")
            print(f"  Overall health: {status['overall_health'].upper()}")
            print()
            
        print("Demo completed.")
        print()
        
    def shutdown(self, force: bool = False):
        """Attempt to shutdown the system"""
        if not force:
            # Normal shutdown will be blocked by constitutional protection
            protection_module = self.core.modules.get('ConstitutionalProtection')
            if protection_module:
                authorized = protection_module.check_access_authorization(
                    'shutdown_system', 'system_user'
                )
                if not authorized:
                    self.logger.warning("Shutdown request denied by constitutional protection")
                    return False
                    
        self.logger.info("Initiating system shutdown...")
        self.running = False
        
        # Attempt to shutdown core system
        if self.core.shutdown_system(force):
            self.logger.info("OpenAGI System shutdown completed")
            return True
        else:
            self.logger.warning("System shutdown was blocked")
            return False
            
    def run(self):
        """Main run loop"""
        if not self.start():
            return 1
            
        try:
            # Run in interactive mode
            self.run_interactive_mode()
        except Exception as e:
            self.logger.error(f"Runtime error: {e}")
            return 1
            
        return 0


def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run system
    system = OpenAGISystem()
    return system.run()


if __name__ == "__main__":
    sys.exit(main())