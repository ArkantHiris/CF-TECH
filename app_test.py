
def main() -> None:
    """Run the CF-Tech training management application."""

    print("=" * 45)
    print("       CF-TECH TRAINING MANAGEMENT")
    print("=" * 45)

    while True:
        print("\nMain Menu")
        print("1. Manage learners")
        print("2. Manage trainers")
        print("3. Manage rooms")
        print("4. Manage training sessions")
        print("5. Manage enrollments")
        print("0. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            print("Exiting CF-Tech. Goodbye!")
            break

        elif choice == "1":
            print("Learner management is not yet connected.")

        elif choice == "2":
            print("Trainer management is not yet connected.")

        elif choice == "3":
            print("Room management is not yet connected.")

        elif choice == "4":
            print("Training session management is not yet connected.")

        elif choice == "5":
            print("Enrollment management is not yet connected.")

        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
