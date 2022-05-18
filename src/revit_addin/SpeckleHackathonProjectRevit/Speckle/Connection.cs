﻿using Speckle.Core.Api;
using Speckle.Core.Credentials;
using Speckle.Core.Models;
using Speckle.Core.Transports;
using SpeckleHackathonProjectRevit.Entities;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace SpeckleHackathonProjectRevit.Speckle
{
    public static class Connection
    {
        public static List<Request> Requests = new List<Request>();
        public static async Task TaskAsync()
        {
            string streamId = Environment.GetEnvironmentVariable("streamId");
            var branchName = "main";
            Account account = new Account();
            account.token = Environment.GetEnvironmentVariable("api_token");
            ServerInfo serverInfo = new ServerInfo();
            serverInfo.url = "https://speckle.xyz/";
            account.serverInfo = serverInfo;
            var client = new Client(account);
            var branch = await client.StreamGetCommits(streamId, 10);
            List<string> referencedObjects = new List<string>();
            foreach (Commit commit in branch)
            {
                referencedObjects.Add(commit.referencedObject);
            }
            var transport = new ServerTransport(account, streamId);
            foreach (string referencedObject in referencedObjects)
            {
                var data = await Operations.Receive(
                                                  referencedObject,
                                                  remoteTransport: transport,
                                                  disposeTransports: true
                                                );
                foreach (var instance in data.GetMembers())
                {
                    try
                    {
                        Dictionary<string, object> dict = (Dictionary<string, object>)instance.Value;
                        string unit = dict.Where(pair => pair.Key == "unit").Select(pair => pair.Value).FirstOrDefault().ToString();
                        string field = dict.Where(pair => pair.Key == "field").Select(pair => pair.Value).FirstOrDefault().ToString();
                        string answer = dict.Where(pair => pair.Key == "answer").Select(pair => pair.Value).FirstOrDefault().ToString();
                        string number = dict.Where(pair => pair.Key == "number").Select(pair => pair.Value).FirstOrDefault().ToString();
                        string element = dict.Where(pair => pair.Key == "element").Select(pair => pair.Value).FirstOrDefault().ToString();
                        string success = dict.Where(pair => pair.Key == "success").Select(pair => pair.Value).FirstOrDefault().ToString();
                        string direction = dict.Where(pair => pair.Key == "direction").Select(pair => pair.Value).FirstOrDefault().ToString();
                        string element_name = dict.Where(pair => pair.Key == "element_name").Select(pair => pair.Value).FirstOrDefault().ToString();

                        if (element_name != "beam")
                        {
                            bool successBool = false;
                            if (success == "true")
                                successBool = true;

                            double numberDouble = Convert.ToDouble(number);
                            if (unit == "m")
                                numberDouble = numberDouble * 3.28084;
                            if (unit == "cm")
                                numberDouble = numberDouble * 0.0328084;
                            numberDouble = Math.Round(numberDouble, 2);

                            Request request = new Request(field, successBool, element, element_name, direction, numberDouble, unit, answer);
                            Requests.Add(request);
                        }                        
                    }
                    catch { }
                }

            }

        }
    }
}
