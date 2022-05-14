using Autodesk.Revit.DB;
using SpeckleHackathonProjectRevit.Commands;
using SpeckleHackathonProjectRevit.Entities;
using System.Linq;

namespace SpeckleHackathonProjectRevit.Tests
{
    public class BeamTests
    {
        public Request RequestItem = RequestsTest.GetTestRequest();
        public Document doc { get; set; }

        public BeamCommand setupTests()
        {
            BeamCommand beamCommand = new BeamCommand(RequestItem, doc);
            beamCommand.GetElements();
            return beamCommand;
        }

        public bool GetElementsShouldReturnSix()
        {
            BeamCommand beamCommand = setupTests();
            return beamCommand.Elements.Count() == 6;
        }

        public bool MoveElement20cmDown()
        {
            BeamCommand beamCommand = setupTests();
            beamCommand.MoveDown();
            return true;
        }

        public bool MoveElement20cmUp()
        {
            BeamCommand beamCommand = setupTests();
            beamCommand.MoveUp();
            return true;
        }

        public bool MoveElement20cmRight()
        {
            BeamCommand beamCommand = setupTests();
            beamCommand.MoveRight();
            return true;
        }

        public bool MoveElement20cmLeft()
        {
            BeamCommand beamCommand = setupTests();
            beamCommand.MoveLeft();
            return true;
        }
    }
}
