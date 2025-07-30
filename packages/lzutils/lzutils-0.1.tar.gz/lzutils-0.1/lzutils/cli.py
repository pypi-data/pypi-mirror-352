def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: lz <your_input>")
        sys.exit(1)

    user_input = sys.argv[1]
    print(f"Received input: {user_input}")
