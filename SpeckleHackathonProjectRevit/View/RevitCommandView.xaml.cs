using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
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
        public RevitCommandView(UIDocument uiDocument, Window win)
        {
            InitializeComponent();            
            uidoc = uiDocument;
            doc = uidoc.Document;
            window = win;
        }

        private void getRequests_Click(object sender, RoutedEventArgs e)
        {
            List<Request> requests = Connection.Requests;
            datagrid.ItemsSource = requests;
        }
    }
}
