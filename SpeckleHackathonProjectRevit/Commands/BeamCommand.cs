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

        public BeamCommand(Request requestItem, Document doc)
        {
            RequestItem = requestItem;
            this.doc = doc;
            GetElements();
        }

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
            XYZ translation = new XYZ(RequestItem.Number, 0, 0);
            foreach (Element element in Elements)
            {
                ElementTransformUtils.MoveElement(doc, element.Id, translation);
                //ChangeElementColor(element.Id);
            } 
        }
        public void MoveLeft()
        {
            XYZ translation = new XYZ(-RequestItem.Number, 0, 0);
            foreach (Element element in Elements)
            {
                ElementTransformUtils.MoveElement(doc, element.Id, translation);
                //ChangeElementColor(element.Id);
            }
        }
        public void MoveUp()
        {
            XYZ translation = new XYZ(0, RequestItem.Number, 0);
            foreach (Element element in Elements)
            {
                ElementTransformUtils.MoveElement(doc, element.Id, translation);
                //ChangeElementColor(element.Id);
            }
        }

        public void MoveDown()
        {
            XYZ translation = new XYZ(0, -RequestItem.Number, 0);
            foreach (Element element in Elements)
            {
                ElementTransformUtils.MoveElement(doc, element.Id, translation);
                //ChangeElementColor(element.Id);
            }
        }

        public void ChangeElementColor(ElementId elementId)
        {
            Autodesk.Revit.DB.View view = doc.ActiveView;
            OverrideGraphicSettings graphicSettings = new OverrideGraphicSettings();
            graphicSettings.SetSurfaceForegroundPatternColor(new Color(255, 128, 64));
            var fillPatternElements = new FilteredElementCollector(doc).OfClass(typeof(FillPatternElement)).FirstOrDefault();
            var filter = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).Where(x => x.Id == elementId);
            graphicSettings.SetSurfaceForegroundPatternId(fillPatternElements.Id);
            //view.SetFilterOverrides(filter., graphicSettings);
        }
    }
}
