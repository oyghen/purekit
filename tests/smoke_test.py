import purekit


def main() -> None:
    result = purekit.__name__
    expected = "purekit"
    if result == expected:
        print(f"Smoke test for {purekit.__name__}: PASSED")
    else:
        raise RuntimeError(f"Smoke test for {purekit.__name__}: FAILED")


if __name__ == "__main__":
    main()
