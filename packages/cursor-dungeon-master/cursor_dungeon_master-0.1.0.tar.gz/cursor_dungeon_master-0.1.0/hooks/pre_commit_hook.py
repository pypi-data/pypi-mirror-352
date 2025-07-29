#!/usr/bin/env python3
"""
Pre-commit hook for Dungeon Master context tracking.

This script integrates with Cursor to enforce context documentation:
- Blocks commits when tracked files lack proper context documentation
- Generates templates for Cursor to fill
- Validates that templates have been meaningfully completed
"""

import sys
import logging
from pathlib import Path
from typing import List, Tuple, Dict

# Add the parent directory to the path so we can import dungeon_master
sys.path.insert(0, str(Path(__file__).parent.parent))

from dungeon_master import (
    parse_tracked_files,
    ensure_output_directory,
    get_git_changes
)
from dungeon_master.generator import generate_context_template
from dungeon_master.updater import (
    validate_context_document,
    get_validation_status,
    get_blocking_issues,
    add_changelog_entry
)
from dungeon_master.utils import write_file_content

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def process_new_tracked_files(tracked_files: Dict[str, str], output_dir: Path) -> Tuple[List[str], List[str]]:
    """
    Process newly tracked files by creating templates.
    
    Args:
        tracked_files: Dictionary mapping file_path -> context_document_name
        output_dir: Output directory for context documents
        
    Returns:
        Tuple[List[str], List[str]]: (created_templates, failed_creations)
    """
    created_templates = []
    failed_creations = []
    
    for file_path, context_doc_name in tracked_files.items():
        context_doc_path = output_dir / context_doc_name
        
        if not context_doc_path.exists():
            # Create new template
            logger.info(f"Creating context template: {context_doc_path}")
            template_content = generate_context_template(file_path)
            
            if template_content:
                success = write_file_content(str(context_doc_path), template_content)
                if success:
                    created_templates.append(context_doc_name)
                else:
                    failed_creations.append(context_doc_name)
            else:
                failed_creations.append(context_doc_name)
    
    return created_templates, failed_creations


def update_existing_documents(tracked_files: Dict[str, str], output_dir: Path) -> List[str]:
    """
    Update existing context documents with changelog entries for file changes.
    
    Args:
        tracked_files: Dictionary mapping file_path -> context_document_name
        output_dir: Output directory for context documents
        
    Returns:
        List[str]: List of documents that were updated
    """
    updated_documents = []
    
    for file_path, context_doc_name in tracked_files.items():
        context_doc_path = output_dir / context_doc_name
        
        if context_doc_path.exists():
            # Check if document is valid before updating
            is_valid, _ = validate_context_document(str(context_doc_path))
            
            if is_valid:
                # Add changelog entry for the file modification
                success = add_changelog_entry(str(context_doc_path), file_path)
                if success:
                    updated_documents.append(context_doc_name)
                    logger.info(f"Added changelog entry to: {context_doc_name}")
    
    return updated_documents


def print_commit_blocked_message(validation_status: Dict[str, Dict[str, any]], 
                                created_templates: List[str],
                                blocking_issues: List[str]):
    """
    Print a comprehensive message explaining why the commit was blocked.
    
    Args:
        validation_status: Validation status for all tracked files
        created_templates: List of newly created templates
        blocking_issues: List of issues blocking the commit
    """
    print("\n" + "=" * 70)
    print("🛡️  COMMIT BLOCKED: Context Documentation Required")
    print("=" * 70)
    
    if created_templates:
        print("\n📝 New context templates created:")
        for template in created_templates:
            print(f"   • dungeon_master/{template}")
    
    if blocking_issues:
        print("\n❌ Issues requiring attention:")
        for issue in blocking_issues:
            print(f"   • {issue}")
    
    print("\n🎯 Next Steps:")
    print("   1. Use Cursor to complete the context documentation")
    print("   2. Fill in all placeholder text marked with parentheses")
    print("   3. Remove the 'Instructions for Cursor' block when done")
    print("   4. Commit again once documentation is complete")
    
    # Show specific guidance for each problematic file
    has_templates = False
    for file_path, status in validation_status.items():
        if not status['valid']:
            if not has_templates:
                print("\n📋 Template completion guide:")
                has_templates = True
            
            print(f"\n   File: {file_path}")
            print(f"   Context: dungeon_master/{status['context_doc']}")
            if status['issues']:
                print(f"   Issues: {', '.join(status['issues'])}")
    
    print("\n💡 Tip: This system helps Cursor maintain accurate, up-to-date")
    print("   repository documentation as you develop!")
    print("=" * 70)


def print_success_message(tracked_files: Dict[str, str], updated_documents: List[str]):
    """
    Print a success message when all validations pass.
    
    Args:
        tracked_files: Dictionary of tracked files
        updated_documents: List of documents that were updated
    """
    print("\n✅ Dungeon Master Context Tracking: All validations passed")
    
    if tracked_files:
        print(f"   📊 Processed {len(tracked_files)} tracked file(s)")
        
        if updated_documents:
            print(f"   📝 Updated {len(updated_documents)} context document(s)")
            for doc in updated_documents:
                print(f"      • {doc}")
    
    print("   🎯 Repository context documentation is up to date!")


def main() -> int:
    """
    Main entry point for the pre-commit hook.
    
    Returns:
        int: Exit code (0 for success, non-zero to block commit)
    """
    logger.info("Dungeon Master pre-commit hook started")
    
    try:
        # Get staged files from Git
        staged_files, new_files = get_git_changes()
        all_changed_files = list(set(staged_files + new_files))
        
        if not all_changed_files:
            logger.info("No staged files found")
            return 0
        
        logger.info(f"Found {len(all_changed_files)} changed files")
        
        # Parse tracked files
        tracked_files = parse_tracked_files(all_changed_files)
        
        if not tracked_files:
            logger.info("No tracked files found in staged changes")
            return 0
        
        logger.info(f"Found {len(tracked_files)} tracked files:")
        for file_path, context_doc in tracked_files.items():
            logger.info(f"  {file_path} -> {context_doc}")
        
        # Ensure output directory exists
        output_dir = ensure_output_directory()
        
        # Process new tracked files (create templates)
        created_templates, failed_creations = process_new_tracked_files(tracked_files, output_dir)
        
        if failed_creations:
            print(f"\n❌ Failed to create templates for: {', '.join(failed_creations)}")
            return 1
        
        # Get validation status for all tracked files
        validation_status = get_validation_status(tracked_files, output_dir)
        
        # Check for blocking issues
        blocking_issues = get_blocking_issues(validation_status)
        
        if blocking_issues or created_templates:
            # Block the commit and provide guidance
            print_commit_blocked_message(validation_status, created_templates, blocking_issues)
            return 1
        
        # If we get here, all validations passed
        # Update existing documents with changelog entries
        updated_documents = update_existing_documents(tracked_files, output_dir)
        
        # Print success message
        print_success_message(tracked_files, updated_documents)
        
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error in pre-commit hook: {e}")
        print(f"\n❌ Dungeon Master hook failed: {e}")
        print("Please check the hook configuration and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 