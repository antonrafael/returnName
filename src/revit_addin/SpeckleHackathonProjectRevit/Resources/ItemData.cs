using Autodesk.Revit.UI;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Media.Imaging;

namespace SpeckleHackathonProjectRevit.Resources
{
    public static class ItemData
    {
        public static PushButton CreateButtom(string fullName, string Location, string commandTitle, string commandDescription, RibbonPanel panel)
        {
            string RibbonImageUri = "/SpeckleHackathonProjectRevit;component/Resources/images/icon16.png";
            string RibbonLargeImageUri = "/SpeckleHackathonProjectRevit;component/Resources/images/icon32.png";

            PushButtonData itemData = new PushButtonData(fullName, commandTitle, Location, fullName);
            PushButton showButton = panel.AddItem(itemData) as PushButton;
            showButton.ToolTip = commandDescription;
            showButton.Image = new BitmapImage(new Uri(RibbonImageUri, UriKind.RelativeOrAbsolute));
            showButton.LargeImage = new BitmapImage(new Uri(RibbonLargeImageUri, UriKind.RelativeOrAbsolute));
            showButton.Enabled = false;

            return showButton;
        }
    }
}
