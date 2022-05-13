using SpeckleHackathonProjectRevit.Entities;
using System;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;

namespace SpeckleHackathonProjectRevit.Tests
{
    public static class RequestsTest
    {
        public static Request GetTestRequest()
        {
            return
                new Request("structural", true, "beam", "B1", "down", 0.2, "m", "Answer");
            
        }
    }
}
