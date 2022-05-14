using System;
using System.IO;
using System.Windows;

namespace SpeckleHackathonProjectRevit
{
    public static class DotEnv
    {
        public static void Load()
        {
            var root = "";
            var dotenv = Path.Combine(root, ".env");
            if (!File.Exists(dotenv))
                return;

            foreach (var line in File.ReadAllLines(dotenv))
            {
                var parts = line.Split('=');

                if (parts.Length != 2)
                    continue;

                Environment.SetEnvironmentVariable(parts[0], parts[1]);
            }
        }
    }
}

