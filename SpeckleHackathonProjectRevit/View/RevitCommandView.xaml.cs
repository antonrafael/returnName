using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using SpeckleHackathonProjectRevit.Commands;
using SpeckleHackathonProjectRevit.Entities;
using SpeckleHackathonProjectRevit.Speckle;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace SpeckleHackathonProjectRevit.View
{
    /// <summary>
    /// Interaction logic for RevitCommandView.xaml
    /// </summary>
    public partial class RevitCommandView : UserControl
    {
        private UIDocument uidoc;
        private Document doc;
        private Window window;
        private List<Request> Requests;
        public RevitCommandView(UIDocument uiDocument, Window win)
        {
            InitializeComponent();            
            uidoc = uiDocument;
            doc = uidoc.Document;
            window = win;           
        }

        private void getRequests_click(object sender, RoutedEventArgs e)
        {
            Requests = Connection.Requests;
            datagrid.ItemsSource = Requests;
        }

      
        private void acceptChanges_click(object sender, RoutedEventArgs e)
        {
            BeamHandler beamHandler = new BeamHandler();
            beamHandler.Requests = Requests.Where(x => x.Check && x.Element == "beam").ToList();
            beamHandler.doc = doc;
            beamHandler.Handle();
        }
    }
}
