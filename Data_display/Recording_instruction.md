### Recording Instruction
- *Display* 按键设置为*Enabled*，这样提供的功能可以保证用户在即使没有开启记录功能，也可以观看上次的飞行记录，同时开发较为简单。
- 为了便于开发，需要对源码进行修改，保证所有的数据可以直接保存在飞行记录的文本文件里。修改如下：
    - 在`.\Plugins\AirSim\Source\Vehicles\Multirotor`目录下找到`MultirotorPawnSimApi.cpp`文件
    - 将函数内容作出如下改动： 
    ```c++
        std::string MultirotorPawnSimApi::getRecordFileLine(bool is_header_line) const
        {
        std::string common_line = PawnSimApi::getRecordFileLine(is_header_line);
        if (is_header_line) {
            return common_line +
                "Latitude\tLongitude\tAltitude\tPressure\tAccX\tAccY\tAccZ\t";
        }

        const auto& state = vehicle_api_->getMultirotorState();
        const auto& bar_data = vehicle_api_->getBarometerData("");
        const auto& imu_data = vehicle_api_->getImuData("");

        std::ostringstream ss;
        ss << common_line;
        ss << state.gps_location.latitude << "\t" << state.gps_location.longitude << "\t"
        << state.gps_location.altitude << "\t";

        ss << bar_data.pressure << "\t";

        ss << imu_data.linear_acceleration.x() << "\t" << imu_data.linear_acceleration.y() << "\t"
        << imu_data.linear_acceleration.z() << "\t";

        return ss.str();
    }
    ```
    - 在同目录下找到`MultirotorPawnSimApi.hpp`文件
    - 添加代码：`virtual std::string getRecordFileLine(bool is_header_line) const override;`
    - 通过C++项目编译后启动Unreal项目
- 在display功能固定展示了上述的数据，故这些数据必须要存在，目前没有做成可选的形式，因此如果找不到上述数据会报错。