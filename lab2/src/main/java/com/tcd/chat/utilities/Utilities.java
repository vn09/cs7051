package com.tcd.chat.utilities;

import java.net.InetAddress;
import java.net.UnknownHostException;

/**
 * Created by vuongnguyen on 27/10/2016.
 */
public class Utilities {
    public static String getLocalHostIP() {
        InetAddress ipAddress = null;
        try {
            ipAddress = InetAddress.getLocalHost();
        } catch (UnknownHostException e) {
            e.printStackTrace();
        }
        return ipAddress.getHostAddress();
    }
}
