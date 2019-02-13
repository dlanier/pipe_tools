###########################
#              AAA_T2IdxArray.wdl
* Demonstrate multi-sample-multilane input indexing correctness
# Usage: clone to run directory
# java -jar ${CROMWELL} run MayomicsVC/src/wdl/SomaticVC/AAA_T2IdxArray.wdl -i MayomicsVC/src/wdl/SomaticVC/AAA_json.json
###########################

task hello {
  String addressee
  Int One
  Int Two
  Int Three
  Int sIx
  command {
    echo "Input String =  ${addressee} With Iterator Index: ${sIx}  [${One}][${Two}][${Three}]"
  }
  output {
    String message = read_string(stdout())
  }
}

workflow wf_hello {

  Array[Array[Array[String]]] ImpString
  Int arr1_size = length(ImpString)
  Int arr2_size = length(ImpString[0])
  Int arr3_size = length(ImpString[0][0])

  Array[Int] Index = range(arr1_size * arr2_size * arr3_size)

  scatter (idx in Index) {

    Int reads_idx = idx % arr3_size

    Int lanes_idx = (idx / arr2_size) % arr2_size

    Int samples_idx = (idx / (arr3_size * arr2_size)) % arr1_size

    call hello as howdy {
      input:
        addressee = ImpString[samples_idx][lanes_idx][reads_idx],
        One = samples_idx,
        Two = lanes_idx,
        Three = reads_idx,
        sIx = idx
    }
  }

  output {
     howdy.message
  }
}

