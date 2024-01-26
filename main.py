import getData
import json_to_csv
import Calculate
import Agent

if __name__ == '__main__':
    getData.main()
    print("getData done")
    json_to_csv.main()
    print("json_to_csv done")
    Calculate.main()
    print("Calculate done")
    Agent.main()
