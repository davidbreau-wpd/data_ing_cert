import logging, os, subprocess
from pathlib import Path

class Lake:
    def _run(self, command, path=Path(__file__).parent.parent / "terraform" / "lake" / "generator"):
        os.chdir(path)
        result = subprocess.run(command, shell=True)
        return result.returncode

    def init(self):
        self._run("terraform init")

    def plan(self):
        self._run("terraform plan -out=tfplan")
        
    def apply(self):
        self._run("terraform apply tfplan")
        
    def destroy(self):
        confirm = input("\n⚠️ Are you sure you want to destroy all resources? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
        self._run("terraform destroy -auto-approve")
        logging.info("✅ Resources destroyed")

    def empty_container(self, container_name="service-reports"):
        account_key = self._run(
            "az storage account keys list --account-name wpdwindmanagerfradls --query [0].value -o tsv"
        )
        confirm = input(f"\n⚠️ Are you sure you want to empty container '{container_name}'? (y/N): ")
        if confirm.lower() != 'y':
            raise Exception("❌ Operation cancelled by user")
        self._run(f"az storage blob delete-batch --source {container_name} --account-name wpdwindmanagerfradls --account-key {account_key}")
        logging.info("🗑️ Container emptied")

    def output(self):
        self._run("terraform output")       

    def deploy(self):
        self.init()
        self.plan()
        self.apply()

    def save_outputs(self):
        root_path = Path(__file__).parent.parent
        os.chdir(root_path)
        self._run("""
echo DATALAKE_CLIENT_ID=$(cd terraform/lake/generator && terraform output -raw sp_datalake_id) > .env
echo DATALAKE_CLIENT_SECRET=$(cd terraform/lake/generator && terraform output -raw sp_datalake_password) >> .env
echo KEYVAULT_CLIENT_ID=$(cd terraform/lake/generator && terraform output -raw sp_keyvault_id) >> .env
echo KEYVAULT_CLIENT_SECRET=$(cd terraform/lake/generator && terraform output -raw sp_keyvault_password) >> .env
""", path=root_path)
        logging.info("✅ Outputs sauvegardés dans .env")
