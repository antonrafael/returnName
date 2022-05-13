using Autodesk.Revit.DB;
using SpeckleHackathonProjectRevit.Entities;
using System;
using System.Collections.Generic;
using System.Linq;

namespace SpeckleHackathonProjectRevit.Commands
{
    public class BeamCommand
    {
        public Guid Id { get; set; }
        public string Name { get; set; }
        public IEnumerable<Element> Elements { get; set; }
        public Request RequestItem { get; set; }
        public Document doc { get; set; }

        public void GetElements()
        {
            Elements = new FilteredElementCollector(doc).
                OfCategory(BuiltInCategory.OST_StructuralFraming).
                WhereElementIsNotElementType().
                ToElements().
                Where(x => {
                    ElementId typeId = x.GetTypeId();
                    return doc.GetElement(typeId).get_Parameter(BuiltInParameter.WINDOW_TYPE_ID).AsString() == RequestItem.ElementName;
                    });
        }
        public void MoveRight()
        {
            XYZ translation = new XYZ(RequestItem.Number * 3.28084, 0, 0);
            foreach (Element element in Elements)
            {
                ElementTransformUtils.MoveElement(doc, element.Id, translation);
            } 
        }
        public void MoveLeft()
        {
            XYZ translation = new XYZ(-RequestItem.Number * 3.28084, 0, 0);
            foreach (Element element in Elements)
            {
                ElementTransformUtils.MoveElement(doc, element.Id, translation);
            }
        }
        public void MoveUp()
        {
            XYZ translation = new XYZ(0, RequestItem.Number * 3.28084, 0);
            foreach (Element element in Elements)
            {
                ElementTransformUtils.MoveElement(doc, element.Id, translation);
            }
        }

        public void MoveDown()
        {
            XYZ translation = new XYZ(0, -RequestItem.Number * 3.28084, 0);
            foreach (Element element in Elements)
            {
                ElementTransformUtils.MoveElement(doc, element.Id, translation);
            }
        }
    }
}
