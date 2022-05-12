using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using SpeckleHackathonProjectRevit.View;
using System;
using System.Windows;

namespace SpeckleHackathonProjectRevit.Commands
{

    [Autodesk.Revit.Attributes.Transaction(Autodesk.Revit.Attributes.TransactionMode.Manual)]
    [Autodesk.Revit.Attributes.Regeneration(Autodesk.Revit.Attributes.RegenerationOption.Manual)]

    public class RevitCommand : IExternalCommand
    {
        public static Window RevitCommandWindow { get; set; }

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            //Get UIDocument
            UIDocument uidoc = commandData.Application.ActiveUIDocument;
            //GetDocument
            Document doc = uidoc.Document;

            try
            {
                RevitCommandWindow = new Window()
                {
                    Width = 450,
                    Height = 800,
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
    }
}
