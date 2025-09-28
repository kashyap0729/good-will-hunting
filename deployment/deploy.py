"""
Deployment Scripts and Utilities
Automated deployment and management scripts for the donation platform
"""

import subprocess
import sys
import json
import time
import argparse
from typing import Dict, List, Optional

class DeploymentManager:
    """Manage deployment process and verification"""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.services = {
            "donation-service": 8000,
            "points-service": 8001,
            "donor-engagement-agent": 8080,
            "charity-optimization-agent": 8081
        }
    
    def deploy_infrastructure(self):
        """Deploy infrastructure using Terraform"""
        print("🏗️  Deploying infrastructure with Terraform...")
        
        # Initialize Terraform
        subprocess.run([
            "terraform", "init"
        ], cwd="infrastructure/terraform", check=True)
        
        # Plan deployment
        subprocess.run([
            "terraform", "plan",
            f"-var=project_id={self.project_id}",
            f"-var=region={self.region}"
        ], cwd="infrastructure/terraform", check=True)
        
        # Apply deployment
        subprocess.run([
            "terraform", "apply",
            "-auto-approve",
            f"-var=project_id={self.project_id}",
            f"-var=region={self.region}"
        ], cwd="infrastructure/terraform", check=True)
        
        print("✅ Infrastructure deployed successfully")
    
    def trigger_cloud_build(self, branch: str = "main"):
        """Trigger Cloud Build deployment"""
        print(f"🚀 Triggering Cloud Build for branch: {branch}")
        
        result = subprocess.run([
            "gcloud", "builds", "submit",
            "--config=cloudbuild.yaml",
            f"--substitutions=_REGION={self.region},_ENVIRONMENT=dev",
            "--project", self.project_id
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Cloud Build triggered successfully")
            build_id = self.extract_build_id(result.stdout)
            if build_id:
                print(f"📊 Build ID: {build_id}")
                self.monitor_build(build_id)
        else:
            print(f"❌ Cloud Build failed: {result.stderr}")
            sys.exit(1)
    
    def extract_build_id(self, stdout: str) -> Optional[str]:
        """Extract build ID from gcloud output"""
        for line in stdout.split('\n'):
            if 'ID:' in line:
                return line.split('ID:')[1].strip()
        return None
    
    def monitor_build(self, build_id: str):
        """Monitor Cloud Build progress"""
        print(f"⏳ Monitoring build {build_id}...")
        
        while True:
            result = subprocess.run([
                "gcloud", "builds", "describe", build_id,
                "--format=json",
                "--project", self.project_id
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                build_info = json.loads(result.stdout)
                status = build_info.get('status', 'UNKNOWN')
                
                if status == 'SUCCESS':
                    print("✅ Build completed successfully")
                    break
                elif status == 'FAILURE':
                    print("❌ Build failed")
                    sys.exit(1)
                elif status in ['CANCELLED', 'TIMEOUT']:
                    print(f"⚠️  Build {status.lower()}")
                    sys.exit(1)
                else:
                    print(f"🔄 Build status: {status}")
                    time.sleep(30)
            else:
                print("❌ Failed to get build status")
                break
    
    def verify_deployment(self):
        """Verify all services are deployed and healthy"""
        print("🔍 Verifying deployment...")
        
        # Get service URLs
        service_urls = {}
        for service_name in self.services.keys():
            try:
                result = subprocess.run([
                    "gcloud", "run", "services", "describe", service_name,
                    "--region", self.region,
                    "--format=value(status.url)",
                    "--project", self.project_id
                ], capture_output=True, text=True, check=True)
                
                service_urls[service_name] = result.stdout.strip()
                print(f"✅ {service_name}: {service_urls[service_name]}")
                
            except subprocess.CalledProcessError:
                print(f"❌ Failed to get URL for {service_name}")
                return False
        
        # Health check all services
        print("\n🏥 Performing health checks...")
        for service_name, url in service_urls.items():
            if self.health_check(url):
                print(f"✅ {service_name} is healthy")
            else:
                print(f"❌ {service_name} health check failed")
                return False
        
        return True
    
    def health_check(self, url: str) -> bool:
        """Perform health check on a service"""
        import requests
        
        try:
            health_url = f"{url}/health"
            response = requests.get(health_url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Health check error: {e}")
            return False
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("🧪 Running integration tests...")
        
        try:
            result = subprocess.run([
                "python", "-m", "pytest",
                "tests/integration/",
                "-v",
                "--tb=short"
            ], check=True)
            
            print("✅ Integration tests passed")
            return True
            
        except subprocess.CalledProcessError:
            print("❌ Integration tests failed")
            return False
    
    def deploy_monitoring(self):
        """Setup monitoring and alerting"""
        print("📊 Setting up monitoring...")
        
        # Create monitoring dashboard
        try:
            subprocess.run([
                "gcloud", "alpha", "monitoring", "dashboards", "create",
                "--config-from-file=deployment/monitoring/dashboard.json",
                "--project", self.project_id
            ], check=True)
            
            print("✅ Monitoring dashboard created")
            
        except subprocess.CalledProcessError:
            print("⚠️  Failed to create monitoring dashboard")
    
    def full_deployment(self):
        """Run complete deployment process"""
        print("🚀 Starting full deployment process...\n")
        
        steps = [
            ("Deploy Infrastructure", self.deploy_infrastructure),
            ("Trigger Cloud Build", self.trigger_cloud_build),
            ("Verify Deployment", self.verify_deployment),
            ("Setup Monitoring", self.deploy_monitoring),
            ("Run Integration Tests", self.run_integration_tests)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 Step: {step_name}")
            try:
                result = step_func()
                if result is False:
                    print(f"❌ Step failed: {step_name}")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Step failed with error: {e}")
                sys.exit(1)
        
        print("\n🎉 Deployment completed successfully!")
        self.print_deployment_summary()
    
    def print_deployment_summary(self):
        """Print deployment summary"""
        print("\n📊 Deployment Summary:")
        print("=" * 50)
        
        # Get App Engine URL
        try:
            result = subprocess.run([
                "gcloud", "app", "describe",
                "--format=value(defaultHostname)",
                "--project", self.project_id
            ], capture_output=True, text=True, check=True)
            
            app_url = result.stdout.strip()
            print(f"🌐 Dashboard URL: https://{app_url}")
            
        except subprocess.CalledProcessError:
            pass
        
        # Get API Gateway URL
        try:
            result = subprocess.run([
                "gcloud", "api-gateway", "gateways", "describe",
                "donation-platform-gateway",
                "--location", self.region,
                "--format=value(defaultHostname)",
                "--project", self.project_id
            ], capture_output=True, text=True, check=True)
            
            api_url = result.stdout.strip()
            print(f"🔗 API Gateway: https://{api_url}")
            
        except subprocess.CalledProcessError:
            pass
        
        print(f"📈 Monitoring: https://console.cloud.google.com/monitoring/dashboards?project={self.project_id}")
        print(f"📝 Logs: https://console.cloud.google.com/logs?project={self.project_id}")
        print("=" * 50)

def main():
    parser = argparse.ArgumentParser(description="Deploy Donation Platform")
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--region", default="us-central1", help="GCP Region")
    parser.add_argument("--action", choices=["infrastructure", "build", "verify", "full"], 
                       default="full", help="Deployment action")
    
    args = parser.parse_args()
    
    # Verify gcloud authentication
    try:
        subprocess.run(["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Please authenticate with gcloud: gcloud auth login")
        sys.exit(1)
    
    # Create deployment manager
    deployment_manager = DeploymentManager(args.project_id, args.region)
    
    # Execute requested action
    if args.action == "infrastructure":
        deployment_manager.deploy_infrastructure()
    elif args.action == "build":
        deployment_manager.trigger_cloud_build()
    elif args.action == "verify":
        deployment_manager.verify_deployment()
    elif args.action == "full":
        deployment_manager.full_deployment()

if __name__ == "__main__":
    main()