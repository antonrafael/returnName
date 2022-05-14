using SpeckleHackathonProjectRevit.Entities;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using System;

namespace SpeckleHackathonProjectRevit.Commands
{
    public class BeamHandler
    {
        public List<Request> Requests { get; set; }
        public Document doc { get; set; }

        public void Handle()
        {
            Transaction trans = new Transaction(doc, "Changing beam elements");

            trans.Start();

            foreach (Request request in Requests)
            {
                try
                {
                    BeamCommand command = new BeamCommand(request, doc);
                    if (request.Direction == "right")
                        command.MoveRight();

                    if (request.Direction == "left")
                        command.MoveLeft();

                    if (request.Direction == "up")
                        command.MoveUp();

                    if (request.Direction == "down")
                        command.MoveDown();
                }
                catch
                {
                    string name = request.ElementName;
                    TaskDialog.Show("Error", String.Format("It's not possible to move the element {0} or the element does not exist", request.ElementName));
                }

                trans.Commit();
            }
        }
    }
}

