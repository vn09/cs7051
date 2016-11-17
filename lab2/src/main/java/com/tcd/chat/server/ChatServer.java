package com.tcd.chat.server;

import com.tcd.chat.utilities.Utilities;
import org.apache.commons.cli.*;
import org.eclipse.jetty.server.Handler;
import org.eclipse.jetty.server.Request;
import org.eclipse.jetty.server.Server;
import org.eclipse.jetty.server.handler.AbstractHandler;
import org.eclipse.jetty.server.handler.HandlerCollection;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.BufferedReader;
import java.io.IOException;

public class ChatServer extends AbstractHandler {
    public static final String STUDENT_ID = "16314667";
    public static final String KILL_SERVICE = "KILL_SERVICE";
    public static final String HELO = "HELO";

    public static Server SERVER = null;
    public static String HOST_ADDRESS;
    public static int HOST_PORT;

    public static void main(String[] args) throws Exception, ParseException {
        // Parse port from command line
        Options defaultOptions = new Options();
        defaultOptions.addOption("p", "port", true, "Port that server runs on");

        CommandLineParser parser = new DefaultParser();
        CommandLine cmd = parser.parse(defaultOptions, args);

        if (cmd.hasOption("port")) {
            HOST_PORT = Integer.parseInt(cmd.getOptionValue("port"));
        } else {
            throw new ParseException("Please specific port number with param -p or -port");
        }

        HOST_ADDRESS = Utilities.getLocalHostIP();
        System.out.println(HOST_ADDRESS);

        SERVER = new Server(HOST_PORT);
        // Add handlers
        HandlerCollection handlerCollection = new HandlerCollection();
        handlerCollection.setHandlers(new Handler[]
                {
                        new ChatServer()
                });
        SERVER.setHandler(handlerCollection);

        // Start server
        SERVER.start();
        SERVER.join();
    }

    public void handle(String target,
                       Request baseRequest,
                       HttpServletRequest request,
                       HttpServletResponse response)
            throws IOException, ServletException {
        BufferedReader reader = request.getReader();
        StringBuilder builder = new StringBuilder();
        String aux = "";

        while ((aux = reader.readLine()) != null) {
            builder.append(aux);
        }
        String content = builder.toString();

        System.out.println(content);

        // Kill server
        if (content.contains(KILL_SERVICE)) {
            if (SERVER != null) {
                try {
                    SERVER.stop();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        } else if (content.contains((HELO))) {
            response.setContentType("text/html;charset=utf-8");
            response.setStatus(HttpServletResponse.SC_OK);
            baseRequest.setHandled(true);
            response.getWriter().println(content +
                    "IP:\n" +
                    "Port:" + HOST_PORT + "\n" +
                    "StudentID:" + STUDENT_ID + "\n");
        }

    }
}