import sys
import math
import re

# 请求用户输入日志文件的名称
name = input("Please enter the log file name: ")

try:
    with open(name, 'r') as logfile:
        lines = logfile.readlines()

    elefound = False
    magfound = False
    r_velocity_found = False
    nstate = 0
    elevec = []
    magvec = []
    f_values = []  # 用于存储每个态的f值
    r_velocities = []  # 用于存储每个态的R(velocity)值
    current_r_velocities = []  # 临时存储当前状态的R(velocity)值

    # 正则表达式匹配 "Excited State" 行来提取f值
    pattern = re.compile(r'Excited State.*?f=([\d.]+)')

    for line in lines:
        match = pattern.search(line)
        if match:
            f_value = float(match.group(1))
            f_values.append(f_value)

    for line in lines:
        if line.startswith(" Ground to excited state transition electric dipole"):
            elefound = True
            continue
        if elefound:
            if line.startswith("       state"):
                continue
            if line.startswith(" Ground to excited state transition velocity dipole"):
                elefound = False
                continue
            else:
                nstate += 1
                tmplist = list(map(float, line.split()[1:4]))
                tmplist.insert(0, int(line.split()[0]))
                elevec.append(tmplist)

        if line.startswith(" Ground to excited state transition magnetic dipole"):
            magfound = True
            continue
        if magfound:
            if line.startswith("       state"):
                continue
            if line.startswith(" Ground to excited state transition velocity quadru"):
                magfound = False
                break
            else:
                tmplist = list(map(float, line.split()[1:4]))
                tmplist.insert(0, int(line.split()[0]))
                magvec.append(tmplist)

    for line in lines:
        match = pattern.search(line)
        if match:
            f_value = float(match.group(1))
            f_values.append(f_value)

        if line.startswith("       state          XX          YY          ZZ    R(velocity)    E-M Angle"):
            r_velocity_found = True
            continue
        elif r_velocity_found and "1/2[<0|r|b>*<b|rxdel|0> + (<0|rxdel|b>*<b|r|0>)*]" in line:
            r_velocity_found = False
            r_velocities.append(current_r_velocities)
            current_r_velocities = []
            continue
        elif r_velocity_found:
            # 提取每行的第五个数字并保存
            parts = line.split()
            if len(parts) >= 5:
                try:
                    current_r_velocities.append(float(parts[4]))
                except ValueError:
                    print(f"Warning: Could not convert R(velocity) to float in line: {line.strip()}")

    # 输出态的数目，默认输出所有的态
    for i in range(nstate):
        elelist = elevec[i]
        maglist = magvec[i]
        f_value = f_values[i]  # 获取对应的f值
        r_velocity_s = r_velocities[0][i]


        # 计算相关物理量
        X1, Y1, Z1 = elelist[1:4]
        X2, Y2, Z2 = maglist[1:4]
        absmiu_au = (X1**2 + Y1**2 + Z1**2)**0.5
        absmiu = absmiu_au *2.541746 * 100  # Debye or 10^-20 esu cm
        absm_au = (X2**2 + Y2**2 + Z2**2)**0.5
        absm = absm_au * 9.27400968*0.1  # unit 10^-20 erg/G
        dotmium = X1 * X2 + Y1 * Y2 + Z1 * Z2
        costheta = dotmium / (absmiu_au * absm_au)
        theta = math.acos(costheta)  # 解为弧度
        theta_degrees = math.degrees(theta)  # 转换为度
        g = 4*costheta*absmiu*(1E-20)*absm*(1E-20)/((absmiu*(1E-20))**2+(absm*(1E-20))**2)
        R_length = -(
            X1 * 2.541746 * 100 * Y1 * 9.27400968 * 0.1 +
            Z1 * 2.541746 * 100 * X2 * 9.27400968 * 0.1 +
            Y2 * 2.541746 * 100 * Z2 * 9.27400968 * 0.1
        )

        # 输出结果
        print("state     %d" % (i + 1))
        print("f         %f" % f_value)  # 输出对应的f值
        print("R         %f"% r_velocity_s)
        print("absmiu    %f 10^-20 esu cm" % absmiu)
        print("absm      %f 10^-20 erg/G" % absm)
        print("costheta  %f" % costheta)
        print("theta     %f degrees" % theta_degrees)
        print("g         %f" % g)
        print("R(length) %f" % R_length)

        print("   ")


except FileNotFoundError:
    print(f"Error: The file {name} was not found.")
