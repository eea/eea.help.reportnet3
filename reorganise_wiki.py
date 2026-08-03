#!/usr/bin/env python3
"""
Reorganises wiki_output/ into topic folders and fixes attachment paths.

Before:
  wiki_output/
    Architecture.md          (references 'attachments/x.png' — wrong path)
    Architecture/attachments/x.png

After:
  wiki_output/
    03_infrastructure/
      Architecture.md        (references 'Architecture/attachments/x.png')
      Architecture/attachments/x.png
"""

import re
import shutil
from pathlib import Path

WIKI_DIR = Path("/Users/janbliki/Documents/GitHub/R3_documentation/wiki_output")

# ---------------------------------------------------------------------------
# Folder → page slugs mapping
# (slug = filename without .md)
# ---------------------------------------------------------------------------
STRUCTURE = {
    "01_overview": [
        "Reportnet_3_Wiki",
        "Operational_Model",
        "Project_Handbook",
        "Reportnet_3_Changelog",
        "Version_Numbers",
        "ROD",
        "Roles_and_permissions",
        "Shared_documents",
        "Ideas_and_context_to_consider_for_Reportnet_3_from_Reportnet_2",
        "Case_studies_for_BDR",
    ],
    "02_development": [
        "Local_setup",
        "Local_setup_",
        "Local_setup_and_onboarding_material",
        "Local_setup_webforms_",
        "Startup_guide_onboarding",
        "Development_and_Production_tools",
        "JUnit_Mockito_testing",
        "Security_Guideline_for_controller_methods",
        "Suggested_gIt_flow_process_",
        "Acceptance_Test",
        "Performance_tests",
        "Api_Documentation",
        "Feature_process_orchestration",
        "EU_login_documentation",
    ],
    "03_infrastructure": [
        "Architecture",
        "Infrastructure",
        "Environments",
        "Kubernetes_deployment_files",
        "Reportnet_Deployment",
        "AWSNKP_Service_Access",
        "Service_Monitoring",
        "Remote_Service_Connection",
        "Logging_information",
        "Automatic_scaling",
        "Autoscaling_model",
        "Dremio_local_setup",
        "Iceberg_demo",
    ],
    "04_deployment": [
        "Merge_and_deployment_process_for_all_environments",
        "Deployment_procedure_",
        "Release_",
        "Release_and_validation_",
        "Release_manually_",
        "Cancel_release_process",
        "Orchestrator_changes_to_production",
        "Transfer_branch_to_another_environment_",
        "Manualy_uninstall_config_or_preconfig_for_deployment_",
        "Process_sequence",
    ],
    "05_operations": [
        "Operation_guidelines",
        "BackupRestore_plan",
        "BackupRestore_HotSwitch_proposed_",
        "Postgres_daily_backup",
        "Postgres_recovery_in_kubernetes",
        "Replicated_Postgres_troubleshooting",
        "Handle_stuck_jobs",
        "Fix_stuck_processes_",
        "Check_And_Fix_Database_Errors",
        "Materialized_views_update_fails_duplicate_records",
        "Released_data_not_visible_in_public_page",
        "Locate_mongo_record_duplicates",
        "Decode_consul_file",
        "Sort_the_consul_file_",
        "FME_support",
        "FME_processes",
        "Reset_MFA_for_Microsoft_and_WikiD",
    ],
    "06_data_runbooks": [
        "Add_or_Recreate_missing_public_files_in_dataflow",
        "Add_provider_to_dataflow",
        "Clone_dataflow_",
        "Delete_provider_data_from_dataflow",
        "Deletion_of_old_dataflows_in_the_database",
        "Deletion_of_hidden_records_in_dataset_",
        "Delete_bad_records_from_dataset",
        "Manual_deletion_of_data",
        "Manual_deletion_of_data_",
        "Import_Reference_Datasets",
        "Import_file_through_external_integration",
        "Copy_data_collections_to_eu_dataset_problems_",
        "Change_schema_in_Datalakes_",
        "Get_lock_record_information",
        "Admin_push__Create_Permissions__button",
        "As_an_Admin_push__Create_Permissions__button",
        "Create_new_database_in_postgres",
        "Access_containers_with_kubectl",
        "Access_containers_with_kubectl_",
    ],
    "07_validation": [
        "Validation_",
        "Validation_api_endpoints",
        "Validation_Priority_Model",
        "Manual_validation",
        "Check_if_dataflow_validation_is_stuck",
        "Fix_cannot_add_records_for_attachment_field",
        "Fix_export_for_NULL_values",
        "Fix_for_error_creating_a_qc_rule_",
        "Release_and_validation_",   # also listed in deployment — kept here only
    ],
    "08_citus": [
        "Citus_findings_coordinator_workers",
        "Reportnet3_citus_setup",
        "Citus_local_setup",
        "Create_new_dataset_from_code",
        "Add_worker_node",
        "Remove_worker_node",
    ],
    "09_support": [
        "Support_model_and_Functional_escalation",
        "Reportnet_Helpdesk_Services",
        "Service_Level_Agreement",
        "Ticket_templates",
    ],
}

# ---------------------------------------------------------------------------
# Build reverse map: slug → folder
# ---------------------------------------------------------------------------
slug_to_folder = {}
for folder, slugs in STRUCTURE.items():
    for slug in slugs:
        if slug in slug_to_folder:
            print(f"WARNING: '{slug}' appears in both "
                  f"'{slug_to_folder[slug]}' and '{folder}' — keeping first")
        else:
            slug_to_folder[slug] = folder


def fix_attachment_paths(text: str, slug: str) -> str:
    """
    Replace bare  attachments/X  with  {slug}/attachments/X
    so the path is correct whether the md is in a subfolder or not.
    """
    # Match markdown image and link syntax pointing to attachments/
    # e.g. ![alt](attachments/foo.png)  or  [text](attachments/foo.pdf)
    return re.sub(
        r'(\!\[[^\]]*\]|\[[^\]]*\])\(attachments/([^)]+)\)',
        lambda m: f'{m.group(1)}({slug}/attachments/{m.group(2)})',
        text,
    )


def main():
    if not WIKI_DIR.exists():
        print(f"ERROR: {WIKI_DIR} does not exist")
        return

    # Create all target folders
    for folder in STRUCTURE:
        (WIKI_DIR / folder).mkdir(exist_ok=True)

    moved = 0
    skipped = 0
    all_slugs = set(slug_to_folder.keys())

    for md_file in sorted(WIKI_DIR.glob("*.md")):
        slug = md_file.stem
        folder = slug_to_folder.get(slug)

        if folder is None:
            print(f"  (no category) {slug}.md — left in place")
            skipped += 1
            continue

        target_dir = WIKI_DIR / folder

        # 1. Fix attachment paths inside the md file
        text = md_file.read_text(encoding="utf-8")
        att_dir = WIKI_DIR / slug   # e.g. wiki_output/Architecture/
        if att_dir.is_dir():
            text = fix_attachment_paths(text, slug)
        md_file.write_text(text, encoding="utf-8")

        # 2. Move the md file
        dest_md = target_dir / md_file.name
        shutil.move(str(md_file), str(dest_md))

        # 3. Move the attachment directory (if it exists)
        if att_dir.is_dir():
            dest_att = target_dir / slug
            if dest_att.exists():
                shutil.rmtree(str(dest_att))
            shutil.move(str(att_dir), str(dest_att))

        print(f"  {folder}/{slug}.md")
        moved += 1

    print(f"\nDone. {moved} pages moved, {skipped} left uncategorised.")

    # Report anything in STRUCTURE that had no matching file
    for slug in all_slugs:
        folder = slug_to_folder[slug]
        dest = WIKI_DIR / folder / f"{slug}.md"
        if not dest.exists():
            # Check if it was already there before we started (shouldn't happen)
            src = WIKI_DIR / f"{slug}.md"
            if not src.exists():
                print(f"  WARNING: '{slug}.md' listed in structure but not found")


if __name__ == "__main__":
    main()
