using Speckle.Core.Models;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SpeckleHackathonProjectRevit.Speckle
{
    public static class Extensions
    {
        // Flattens a base object into all its constituent parts.
        public static IEnumerable<Base> Flatten(this Base obj)
        {
            yield return obj;

            var props = obj.GetDynamicMemberNames();
            foreach (var prop in props)
            {
                var value = obj[prop];
                if (value == null) continue;

                if (value is Base b)
                {
                    var nested = b.Flatten();
                    foreach (var child in nested) yield return child;
                }

                if (value is IDictionary dict)
                {
                    foreach (var dictValue in dict.Values)
                    {
                        if (dictValue is Base lb)
                        {
                            foreach (var lbChild in lb.Flatten()) yield return lbChild;
                        }
                    }
                }

                if (value is IEnumerable enumerable)
                {
                    foreach (var listValue in enumerable)
                    {
                        if (listValue is Base lb)
                        {
                            foreach (var lbChild in lb.Flatten()) yield return lbChild;
                        }
                    }
                }
            }
        }
    }

}
