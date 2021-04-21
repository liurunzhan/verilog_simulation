/**
  * case : ${case}
  * func : ${description}
  * proj : ${project}
  * vern : ${version}
  * date : ${date}
  */

#include <stdio.h>
#include "${project}.h"

int main(void) 
{
  fprintf(stdout, "test CASE ${case}\n");
  
  return 0;
}