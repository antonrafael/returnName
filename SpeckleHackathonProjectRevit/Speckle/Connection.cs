using System;
using System.Collections.Generic;
using System.Collections;
using System.Linq;
using Speckle.Core.Api;
using Speckle.Core.Models;
using RestSharp;
using GraphQL.Client.Http;
using Speckle.Core.Api.GraphQL.Serializer;
using GraphQL;

namespace SpeckleHackathonProjectRevit.Speckle
{
    public static class Connection
    {
        
        public void GetCommits()
        {
            var graphQLClient = new GraphQLHttpClient("https://api.example.com/graphql", new NewtonsoftJsonSerializer());
            var heroRequest = new GraphQLRequest
            {
                Query = @"
                        query MainCommits{
                          stream(id:""8e6d1d1c53"") {
                            branch(name: ""main""){
                                            commits{
                                            totalCount
                                            items{
                                                id
                                                referencedObject
                                       }
                                    }
                                  } 
                               }
                              }

"
            };


        }

    }
}
