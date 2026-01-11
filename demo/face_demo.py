#!/usr/bin/env python3
"""Face Recognition Demo CLI.

Command-line interface for testing the face recognition system.
Supports enrollment, verification, and identification operations.

Usage:
    python -m demo.face_demo enroll <user_id> <name>
    python -m demo.face_demo verify <user_id>
    python -m demo.face_demo identify
    python -m demo.face_demo list
    python -m demo.face_demo delete <user_id>
    python -m demo.face_demo stats
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.workflows.enrollment import FaceEnrollmentWorkflow
from src.workflows.verification import FaceVerificationWorkflow
from src.database.storage import DatabaseManager


def cmd_enroll(args):
    """Enroll a new user."""
    workflow = FaceEnrollmentWorkflow()
    
    result = workflow.enroll_interactive(
        user_id=args.user_id,
        name=args.name,
        num_samples=args.samples
    )
    
    if result.success:
        print(f"\n✓ Successfully enrolled '{args.name}' ({args.user_id})")
        print(f"  Samples captured: {result.num_samples}")
        return 0
    else:
        print(f"\n✗ Enrollment failed: {result.message}")
        return 1


def cmd_verify(args):
    """Verify a user's identity."""
    workflow = FaceVerificationWorkflow()
    
    result = workflow.verify(
        user_id=args.user_id,
        timeout=args.timeout
    )
    
    # Result already printed in workflow
    if result.success:
        return 0
    else:
        if result.face_score > 0:
            print(f"  Distance threshold: {workflow.face_threshold}")
        return 1


def cmd_identify(args):
    """Identify who is in front of the camera."""
    workflow = FaceVerificationWorkflow()
    
    result = workflow.identify(timeout=args.timeout)
    
    # Result already printed in workflow
    if result.success:
        return 0
    else:
        return 1


def cmd_list(args):
    """List all enrolled users."""
    db = DatabaseManager()
    db.initialize()
    
    users = db.list_users(active_only=not args.all)
    
    if not users:
        print("No users enrolled.")
        return 0
    
    print(f"\nEnrolled Users ({len(users)}):")
    print("-" * 50)
    
    for user in users:
        status = "active" if user.is_active else "inactive"
        print(f"  {user.user_id}: {user.name} [{status}]")
        print(f"    Enrolled: {user.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Check if has face template
        template = db.get_face_template(user.user_id)
        if template:
            print(f"    Face samples: {len(template.encodings)}")
    
    print("-" * 50)
    return 0


def cmd_delete(args):
    """Delete an enrolled user."""
    db = DatabaseManager()
    db.initialize()
    
    user = db.get_user(args.user_id)
    if not user:
        print(f"User '{args.user_id}' not found.")
        return 1
    
    if not args.force:
        confirm = input(f"Delete user '{user.name}' ({args.user_id})? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return 0
    
    if db.delete_user(args.user_id):
        print(f"✓ Deleted user '{user.name}' ({args.user_id})")
        return 0
    else:
        print(f"✗ Failed to delete user")
        return 1


def cmd_stats(args):
    """Show verification statistics."""
    db = DatabaseManager()
    db.initialize()
    
    stats = db.get_verification_stats(
        user_id=args.user_id,
        days=args.days
    )
    
    print(f"\nVerification Statistics (last {args.days} days):")
    print("-" * 50)
    print(f"  Total attempts: {stats['total_attempts']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    
    if stats['avg_face_score'] is not None:
        print(f"  Avg face score: {stats['avg_face_score']:.3f}")
    
    print("-" * 50)
    return 0


def cmd_continuous(args):
    """Run continuous verification/identification."""
    if args.user_id:
        # Continuous verification
        workflow = FaceVerificationWorkflow()
        print(f"\nStarting continuous verification for '{args.user_id}'...")
        print("Press 'q' to quit.\n")
        
        for result in workflow.continuous_verify(args.user_id):
            status = "✓" if result.success else "✗"
            print(f"\r{status} Score: {result.face_score:.3f}", end="", flush=True)
            
            if result.success:
                print(f"\n\n✓ Access granted!")
                break
    else:
        # Continuous identification
        workflow = FaceVerificationWorkflow()
        print("\nStarting continuous identification...")
        print("Press 'q' to quit.\n")
        
        for result in workflow.continuous_identify():
            if result.success:
                print(f"\r✓ {result.user_name} ({result.face_score:.3f})       ", end="", flush=True)
            else:
                print(f"\r  Searching... ({result.face_score:.3f})       ", end="", flush=True)
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Face Recognition Demo CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s enroll john_doe "John Doe"    Enroll a new user
  %(prog)s verify john_doe               Verify user identity
  %(prog)s identify                      Identify who is at camera
  %(prog)s list                          List enrolled users
  %(prog)s delete john_doe               Delete a user
  %(prog)s stats                         Show verification stats
  %(prog)s continuous                    Run continuous identification
  %(prog)s continuous john_doe           Run continuous verification
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Enroll command
    enroll_parser = subparsers.add_parser("enroll", help="Enroll a new user")
    enroll_parser.add_argument("user_id", help="Unique user identifier")
    enroll_parser.add_argument("name", help="User's display name")
    enroll_parser.add_argument(
        "-s", "--samples",
        type=int,
        default=5,
        help="Number of face samples to capture (default: 5)"
    )
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a user's identity")
    verify_parser.add_argument("user_id", help="User ID to verify")
    verify_parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=30.0,
        help="Verification timeout in seconds (default: 30)"
    )
    
    # Identify command
    identify_parser = subparsers.add_parser("identify", help="Identify who is at camera")
    identify_parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=30.0,
        help="Identification timeout in seconds (default: 30)"
    )
    
    # List command
    list_parser = subparsers.add_parser("list", help="List enrolled users")
    list_parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Include inactive users"
    )
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an enrolled user")
    delete_parser.add_argument("user_id", help="User ID to delete")
    delete_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Delete without confirmation"
    )
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show verification statistics")
    stats_parser.add_argument(
        "-u", "--user-id",
        help="Filter by user ID"
    )
    stats_parser.add_argument(
        "-d", "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)"
    )
    
    # Continuous command
    continuous_parser = subparsers.add_parser(
        "continuous",
        help="Run continuous verification/identification"
    )
    continuous_parser.add_argument(
        "user_id",
        nargs="?",
        help="User ID for verification (omit for identification)"
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    # Dispatch to command handler
    commands = {
        "enroll": cmd_enroll,
        "verify": cmd_verify,
        "identify": cmd_identify,
        "list": cmd_list,
        "delete": cmd_delete,
        "stats": cmd_stats,
        "continuous": cmd_continuous,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
