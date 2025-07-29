# 一个简单的python脚本示例，用于测试TaskLauncher的功能
import time

def main():
    print("TaskLauncher Test Script")
    print("This script will run for 10 seconds.")
    
    for i in range(10):
        print(f"Running... {i + 1} seconds")
        time.sleep(1)
    
    print("Test script completed successfully.")

    # 创建一个简单的测试输出
    with open("test_output.txt", "w") as f:
        f.write("This is a test output file created by TaskLauncher example script.\n")
        f.write("It confirms that the script ran successfully.\n")

if __name__ == "__main__":
    main()