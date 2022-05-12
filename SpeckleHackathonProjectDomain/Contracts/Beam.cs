using System;

namespace SpeckleHackathonProjectDomain.Contracts
{
    public abstract class Beam
    {
        public Guid Id { get; set; }
        public int ElementId { get; set; }

        public void GetElement() 
        {
        }
        public GenericResult MoveRight() 
        {
            return new GenericResult(true);
        }
        public GenericResult MoveLeft() 
        {
            return new GenericResult(true);
        }

    }
}
