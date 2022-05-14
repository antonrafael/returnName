using Newtonsoft.Json;

namespace SpeckleHackathonProjectRevit.Entities
{
    public class Request
    {

        public string Field { get; set; }
        public bool Success { get; set; }
        public string Element { get; set; }
        public string ElementName { get; set; }
        public string Direction { get; set; }
        public double Number { get; set; }
        public string Unit { get; set; }
        public string Answer { get; set; }

        public Request(string field, bool success, string element, string elementName, string direction, double number, string unit, string answer)
        {
            Field = field;
            Success = success;
            Element = element;
            ElementName = elementName;
            Direction = direction;
            Number = number;
            Unit = unit;
            Answer = answer;
        }
    }

    
}
