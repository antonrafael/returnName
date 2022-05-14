using System;
using System.IO;
using System.Windows;

namespace SpeckleHackathonProjectRevit
{
    public static class DotEnv
    {
        public static void Load()
        {
            var path = "C:\\dev\\SpeckleHackathonProject\\SpeckleHackathonProjectRevit\\.env";
            if (!File.Exists(path))
                return;

            foreach (var line in File.ReadAllLines(path))
            {
                var parts = line.Split('=');

                if (parts.Length != 2)
                    continue;

                Environment.SetEnvironmentVariable(parts[0], parts[1]);
            }
        }
    }
}

