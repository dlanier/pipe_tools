###########################
#	helloTestArray.wdl
###########################
 
task hello {
  String addressee
  command {
    echo "Hello ${addressee}! Welcome to Cromwell . . . on AWS!"
  }
  output {
    String message = read_string(stdout())
  }
}

workflow wf_hello {
  File array_of_strings
  Array[String] ImpString = ["Huey", "Dewey", "Louie"]
  Array[Int] Index = range(length(ImpString))
  
  scatter (idx in Index)
    call hello as howdy {
      input:
        addressee = ImpString[idx]
    }
  }

  output {
     howdy.message
  }
}