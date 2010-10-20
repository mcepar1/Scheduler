This package contains plug-ins, that extend the core schedulrer's functionality.

How to use and write a plug-in:
 * every plug-in must be a class
 * the constructor accepts the following parameters (in the same order):
   1. people
   2. workplaces
   3. turnuses
   4. date
   5. logger 
 * every plug-in must have a perform_task(overtime) method
   * this method performs the task, that the plug-in was written for
   * the overtime parameter is optional (default False)
   
When will the plug-ins be used:
 * all the plug-ins will be used from the core scheduler
 * their constructor will be called from the core scheduler's constructor
 * the perform_task will be called from each scheduling phase in the core constructor
 
How to make the plug-in usable:
 * add it to the PLUG_INS list in the core scheduler
 * the list is ordered
    