
# Python NLIP Repositories 

This repository contains one component of the various python repositories for NLIP Proof of Concept implementation. The various repositories are: 

* nlip_sdk: this provides a software development kit in python that implements the abstractions of NLIP message, submessages along with a factory to ease the creation of NLIP messages and submessages 
* nlip_client: this provides a package that simplifies the task of sending NLIP messages using the base underlying protocol. The current implementation uses httpx as the base transfer package. 
* nlip_server: this provides a paclage that simplifies the task of writing a server-side NLIP application. This provides the abstractions of a NLIPApplication and a NLIP Session. An application consists of multiple sessions. 

The above three are the components needed to write a client or a server. To write a client, you need to use nlip_sdk and nlip_client. To write a server side application, you need to use nlip_sdk and nlip_server. 

The following repositories contain a few simple clients and server side applications: 

* nlip_soln: this provides a few simple prototype server side solutions using the nlip_server package 
* text_client: this provides a simple text based chatbot to interface with a NLIP server 
* kivy_client: this provides a python kivy based visual client to interact with an NLIP server

# NLIP SDK

The NLIP SDK provides the basic functionality that is needed to implement the NLIP protocol, either on the client side or on the server side. The server side requires additional packages. The NLIP SDK is targeted primarily at NLIP clients. 

The NLIP SDK contains the following modules: 

* utils.py - A set of basic utility routines that simplify implementation. 
* errrors.py - A set of error definitions that help diagnose in development. 
* nlip.py - The definition of the NLIP message formats. 

## Publishing the Package

To publish the package to PyPI, ensure that your changes are committed and then create a version tag. You can do this with the following commands:

```bash
$ git tag v0.1.0  # Replace with new version
$ git push origin v0.1.0
```
