using Newtonsoft.Json;

namespace SpeckleHackathonProjectRevit.Entities
{
    public class Request
    {
        [JsonProperty("field")]
        public string Field { get; set; }

        [JsonProperty("success")]
        public string Success { get; set; }

        [JsonProperty("element")]
        public string Element { get; set; }

        [JsonProperty("element_name")]
        public string ElementName { get; set; }

        [JsonProperty("direction")]
        public string Direction { get; set; }

        [JsonProperty("number")]
        public string Number { get; set; }

        [JsonProperty("unit")]
        public string Unit { get; set; }

        [JsonProperty("answer")]
        public string Answer { get; set; }

    }
}
