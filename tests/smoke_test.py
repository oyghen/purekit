import purekit


def main():
    result = purekit.__name__
    expected = "purekit"
    if result == expected:
        print("smoke test passed")
    else:
        raise RuntimeError("smoke test failed")


if __name__ == "__main__":
    main()
