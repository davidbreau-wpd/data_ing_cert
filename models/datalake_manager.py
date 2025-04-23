import logging,os, subprocess
from pathlib import Path

class Lake:
    def _run(self, command, capture_output=False):
        os.chdir(Path(__file__).parent.parent / "terraform" /"lake" / "generator")
        result = subprocess.run(command, shell=True, capture_output=capture_output)
        return result.stdout.decode('utf-8').strip() if capture_output else result.returncode

    def init(self):
        self._run("terraform init")

    def plan(self):
        self._run("terraform plan -out=tfplan")
        
    def apply(self):
        self._run(f"terraform apply tfplan")
        
    def destroy(self):
        confirm = input("\n⚠️ Are you sure you want to destroy all resources? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
        
        self._run("terraform destroy -auto-approve")
        logging.info("✅ Resources destroyed")

    def empty_container(self, container_name="service-reports"):
        # Get storage account key directly from Azure
        account_key = self._run(
            "az storage account keys list --account-name wpdwindmanagerfradls --query [0].value -o tsv", 
            capture_output=True
        ).strip()
        
        # Security confirmation
        confirm = input(f"\n⚠️ Are you sure you want to empty container '{container_name}'? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
        
        # Empty container with Azure CLI using account key
        self._run(f"az storage blob delete-batch --source {container_name} --account-name wpdwindmanagerfradls --account-key {account_key}")
        logging.info("🗑️ Container emptied")

    def output(self):
        self._run("terraform output")       
        
    def deploy(self):
        self.init()
        self.plan()
        self.apply()
