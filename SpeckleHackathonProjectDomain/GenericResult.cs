namespace SpeckleHackathonProjectDomain
{
    public class GenericResult
    {
        public bool Answer { get; set; }
        public string Message { get; set; }

        public GenericResult(bool answer)
        {
            Answer = answer;
            Message = "Refused";
            if (Answer)
            {
                Message = "Accepted";
            }
        }
    }
}