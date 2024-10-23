#!/usr/bin/env python

import socket
import sys
import logging, os
import time
# import datetime
import threading



import rospy
from std_msgs.msg import String
from sensor_msgs.msg import NavSatFix
from sensor_msgs.msg import TimeReference
from std_msgs.msg import Header

# Geometry message type
from geometry_msgs.msg import Twist
from geometry_msgs.msg import TwistStamped

gps_buf=[]
time_ref_buf=0
gps_vel_buf=[]

def callback_gps(data):
	global gps_buf
	# rospy.loginfo(rospy.get_caller_id() + " GPS: %s, %s, %s, %s", data.latitude, data.longitude, data.altitude, data.header.stamp)

	gps_buf = [data.latitude, data.longitude, data.altitude, int(str(data.header.stamp))]
	print(gps_buf)
	# value = datetime.datetime.fromtimestamp(float(data.header.stamp))
	# print(value.strftime('%Y-%m-%d %H:%M:%S'))

def callback_ts(data):
	global time_ref_buf
	# rospy.loginfo(rospy.get_caller_id() + " TS: %s", data.time_ref)
	time_ref_buf=data.time_ref
	print(time_ref_buf)

def callback_vel(data):
	global gps_vel_buf
	# rospy.loginfo(rospy.get_caller_id() + " Vel: %s", data.twist)
	gps_vel_buf=[[data.twist.linear.x, data.twist.linear.y, data.twist.linear.z], [data.twist.angular.x, data.twist.angular.y, data.twist.angular.z]]
	print(gps_vel_buf)

def subsGPS_T_V():
	rospy.init_node('getGPSInfo', anonymous=False)
	rospy.Subscriber('/mavros/global_position/global', NavSatFix, callback_gps)
	rospy.Subscriber('/mavros/global_position/raw/gps_vel', TwistStamped, callback_vel)
	rospy.Subscriber('/mavros/time_reference', TimeReference, callback_ts)
	
	rospy.spin()


# def sendUDP():

# 	global gps_buf
# 	global gps_vel_buf
# 	global time_ref_buf

# 	# IPv4
# 	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 	# client.settimeout(0.2)

# 	# currSeq = 0
# 	# prevSeq = 0

# 	time.sleep(0.5)

# 	print(gps_buf)
# 	print(gps_vel_buf)
# 	print(time_ref_buf)

# 	while not rospy.is_shutdown():
# 		try:
# 			message = ""
# 			if gps_vel_buf:
# 				if gps_vel_buf[0][0] <= 0.01:
# 					message = "CCM,"
# 				else:
# 					message = "ECM,"
# 			else:
# 				message = "NULL,"

# 			for gpsData in gps_buf:
# 				message = message+str(gpsData) + ","
# 			for velData in gps_vel_buf:
# 				message = message+str(velData)+","

# 			message = message+ str(time_ref_buf)
# 			# message = "CCM,"+str(gps_buf[0]) + ","+str(gps_buf[1]) + ","+str(gps_buf[2]) + ","+str(gps_buf[3]) + "," + str(gps_vel_buf) + "," + str(time_ref_buf)

# 			# prevSeq = currSeq
# 			encodedMsg = message.encode(encoding="utf-8")
# 			print(encodedMsg)
# 			# print(byteData)
# 			client.sendto(encodedMsg, ('10.42.0.1', 37021)) # 2001:db8:100:15a::3
# 			print("message sent!\n")

# 			time.sleep(0.5)

# 		except KeyboardInterrupt:
# 			break


def rcvUDP():
	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	# client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM) # UDP
	# client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	client.bind(("", 37020))
	while not rospy.is_shutdown():
		try:
			currLocalTime = time.time()
			data, addr = client.recvfrom(1024)
			decodedData = data.decode("utf-8")
			splitedDataList = decodedData.split(',')

			delay = currLocalTime-float(splitedDataList[-1])

			print("received message: %s"%decodedData)
			print("Tr - Ts:"+"{:.6f}".format(currLocalTime)+"-"+splitedDataList[-1]+"="+str(delay) +"\n")

			# payload, client_address = sock.recvfrom(1)
			print("Echoing data back to " + str(addr[0]))
			sent = client.sendto(data, (addr[0], 37021) )

		except KeyboardInterrupt:
			break


if __name__ == "__main__":
	# udp sending thread
	# udpSend = threading.Thread(target=sendUDP, args=())
	# udpSend.start()

	# udp receiving thread 
	udpRcv = threading.Thread(target=rcvUDP, args=())
	udpRcv.start()


	# main thread for sensor data
	# subsGPS_T_V()