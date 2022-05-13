using Newtonsoft.Json;

namespace SpeckleHackathonProjectRevit.Entities
{
    public class Request
    {
        [JsonProperty("field")]
        public string Field { get; set; }

        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("element")]
        public string Element { get; set; }

        [JsonProperty("element_name")]
        public string ElementName { get; set; }

        [JsonProperty("direction")]
        public string Direction { get; set; }

        [JsonProperty("number")]
        public double Number { get; set; }

        [JsonProperty("unit")]
        public string Unit { get; set; }

        [JsonProperty("answer")]
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
