using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using SpeckleHackathonProjectRevit.Tests;
using SpeckleHackathonProjectRevit.View;
using SpeckleHackathonProjectRevit.Speckle;
using System;
using System.Windows;
using System.Threading.Tasks;
using System.IO;

namespace SpeckleHackathonProjectRevit.Commands
{

    [Autodesk.Revit.Attributes.Transaction(Autodesk.Revit.Attributes.TransactionMode.Manual)]
    [Autodesk.Revit.Attributes.Regeneration(Autodesk.Revit.Attributes.RegenerationOption.Manual)]

    public class RevitCommand : IExternalCommand
    {
        public static Window RevitCommandWindow { get; set; }
        public bool Tests = true;

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            DotEnv.Load();

            //Get UIDocument
            UIDocument uidoc = commandData.Application.ActiveUIDocument;
            //GetDocument
            Document doc = uidoc.Document;

            using (Transaction trans = new Transaction(doc, "Speckly Changing Elements"))
            {
                trans.Start();

                if (Tests)
                {
                    BeamTests beamTests = new BeamTests();
                    beamTests.doc = doc;
                    //TaskDialog.Show("Collector Test", beamTests.GetElementsShouldReturnSix().ToString());
                    //TaskDialog.Show("MoveDown Test", beamTests.MoveElement20cmDown().ToString());
                    //TaskDialog.Show("MoveUp Test", beamTests.MoveElement20cmUp().ToString());
                    //TaskDialog.Show("MoveRight Test", beamTests.MoveElement20cmRight().ToString());
                    //TaskDialog.Show("MoveLeft Test", beamTests.MoveElement20cmLeft().ToString());
                }
                Run();
                trans.Commit();
                

            }
            try
            {
                RevitCommandWindow = new Window()
                {
                    Width = 800,
                    Height = 550,
                    ResizeMode = 0,
                };

                var viewmodel = new RevitCommandView(uidoc, RevitCommandWindow);
                RevitCommandWindow.Content = viewmodel;
                RevitCommandWindow.ShowDialog();

                return Result.Succeeded;
            }
            catch (Exception e)
            {
                RevitCommandWindow.Close();
                TaskDialog.Show("Error", e.Message);
                return Result.Failed;
            }
        }

        public static async Task Run()
        {
            await Connection.TaskAsync();
        }
    }
}
