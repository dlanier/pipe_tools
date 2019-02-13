#########################################################################
#       This WDL script calls the Mutect WDL Task                      ##

#########################################################################
import "MayomicsVC/src/wdl/Alignment/Tasks/alignment.wdl" as ALIGNMENT

workflow CallAlignmentTask {

   Array[Array[Array[File]]] InputRead_1_Arr
   Array[Array[Array[String]]] InputRead_2_Arr
   Array[String] SampleNames

   Int sample_arr_length = length( InputRead_1_Arr )
   Int lane_arr_length = length( InputRead_1_Arr[0] )
   Int read_arr_length = length( InputRead_1_Arr[0][0] )

   Array[Int] Index = range( sample_arr_length * lane_arr_length * read_arr_length )

   scatter (idx in Index) {
      
      Int reads_idx = idx % read_arr_length
      Int lanes_idx = ( idx / lane_arr_length ) % lane_arr_length
      Int samples_idx = ( idx / ( sample_arr_length * lane_arr_length ) )  % sample_arr_length


      call ALIGNMENT.alignmentTask as alignment {

         input:
             SampleName = SampleNames[samples_idx],
             InputRead1 = InputRead_1_Arr[samples_idx][lanes_idx][reads_idx],
             InputRead2 = InputRead_2_Arr[samples_idx][lanes_idx][reads_idx]

      }
   }
}
