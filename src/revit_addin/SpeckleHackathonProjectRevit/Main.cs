using Autodesk.Revit.UI;
using SpeckleHackathonProjectRevit.Resources;
using System.Collections.Generic;
using System.IO;
using System.Reflection;

namespace SpeckleHackathonProjectRevit
{
    public class Main : IExternalApplication
    {
        public Result OnStartup(UIControlledApplication application)
        {      
            application.CreateRibbonTab("Speckle Hackathon");
            RibbonPanel panel = application.CreateRibbonPanel("Speckle Hackathon", "Requests");
            //List of Push Buttons
            List<PushButton> pushButtons = new List<PushButton>();

            //Furacao Command
            pushButtons.Add(
                ItemData.CreateButtom(typeof(SpeckleHackathonProjectRevit.Commands.RevitCommand).FullName, 
                Assembly.GetAssembly(typeof(SpeckleHackathonProjectRevit.Commands.RevitCommand)).Location, 
                "Specklebot", 
                "Description",
                panel));

            //enable pushButtons
            pushButtons.ForEach(button => button.Enabled = true);

            return Result.Succeeded;
        }

        public Result OnShutdown(UIControlledApplication application)
        {
            return Result.Succeeded;
        }     

    }
}

