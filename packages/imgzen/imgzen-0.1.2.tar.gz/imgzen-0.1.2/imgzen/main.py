import os

import cv2
import picflow.utils as utils
import argparse


def main() -> None:
    command_choices = ["rotate", "resize", "contrast", "blur", "autocorrect"]

    parser = argparse.ArgumentParser(description="Process some images.")

    parser.add_argument("command", choices=command_choices, help="Operation to make")

    parser.add_argument("-i", "--input", required=True, help="Path to input image")
    parser.add_argument("-o", "--output", required=True, help="Path to output image")

    parser.add_argument("-a", "--angle", type=float, default=90.0, help="Rotation angle (for rotate)")
    parser.add_argument("--width", type=int, help="Resized image width (for resize)")
    parser.add_argument("--height", type=int, help="Resized image height (for resize)")
    parser.add_argument("-k", "--ksize", type=int, default=15, help="Blur kernel size (for blur)")

    # add more arguments

    args = parser.parse_args()

    img = cv2.imread(args.input)
    if img is None:
        print(f"Image not found at {args.input}")
        return

    if args.command == "rotate":
        result = utils.rotate_image(img, args.angle)
    elif args.command == "resize":
        result = utils.resize_image(img, width=args.width, height=args.height)
    elif args.command == "contrast":
        result = utils.enhance_contrast(img)
    elif args.command == "blur":
        result = utils.blur_background(img, kernel=(args.ksize, args.ksize))
    elif args.command == "autocorrect":
        result = utils.auto_correction(img)
    else:
        print("Invalid command")

    # Handle result
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    cv2.imwrite(args.output, result)
    print(f"Result saved to {args.output}")


if __name__ == "__main__":
    main()
