/* 
 * Name: Logan Finlayson
 * UPI: lfin100
 * ID: 2969317
 * 
 */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data.Entity;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Assignment2
{
    public class Program
    {
        static void Main(string[] args)
        {
            using (AmbStaffContext db = new AmbStaffContext()) {
                bool running = true;

                while (running)
                {
                    Console.Write(":>");
                    string input = Console.ReadLine();
                    string[] inputArray;
                    inputArray = input.Split();

                    for (int i = 0; i < inputArray.Length; i++)
                    {
                        if (inputArray[i].ToLower() == "as")
                        {
                            inputArray[i] = "AS";
                        }

                        else if (inputArray[i].ToLower() == "to")
                        {
                            inputArray[i] = "TO";
                        }

                        else if (inputArray[i].ToLower() == "id")
                        {
                            inputArray[i] = "ID";
                        }

                    }

                    int IDpos, ASpos, TOpos, staffID;
                    string firstNames, lastName, skillLevel, ambulanceID, staffID_str;

                    switch (inputArray[0].ToLower())
                    {
                        case "add":
                            IDpos = Array.IndexOf(inputArray, "ID");
                            ASpos = Array.IndexOf(inputArray, "AS");

                            if (IDpos == -1)
                            {
                                Console.WriteLine("An officer must have a six digit ID number");
                                break;
                            }

                            if (IDpos < 3)
                            {
                                Console.WriteLine("An officer must have a surname and at least one given name");
                                break;
                            }

                            if (inputArray[IDpos + 1].Length != 6 || !Int32.TryParse(inputArray[IDpos + 1], out staffID))
                            {
                                Console.WriteLine("The officer ID must be a six digit number");
                                break;
                            }

                            if (ASpos == -1)
                            {
                                Console.WriteLine("An officer must have a skill level (basic, intermediate, or advanced");
                                break;
                            }



                            staffID_str = inputArray[IDpos + 1];

                            firstNames = inputArray[1];
                            for (int i = 2; i < IDpos-1; i++)
                            {
                                firstNames += (" " + inputArray[i]);
                            }

                            lastName = inputArray[IDpos - 1];

                            switch (inputArray[ASpos + 1].ToLower())
                            {
                                case "basic":
                                    skillLevel = "Basic";
                                    break;
                                case "intermediate":
                                    skillLevel = "Intermediate";
                                    break;
                                case "advanced":
                                    skillLevel = "Advanced";
                                    break;
                                default:
                                    skillLevel = null;
                                    break;
                            }

                            if (skillLevel == null)
                            {
                                Console.WriteLine("The skill level for the officer must be one of basic, intermediate, or advanced");
                                break;
                            }

                            ADD(db, firstNames, lastName, staffID_str, skillLevel);


                            break;

                        case "remove":
                            if (inputArray.Length != 2 || inputArray[1].Length != 6)
                            {
                                Console.WriteLine("The input must be a single 6 digit staff ID number");
                                break;
                            }

                            if (!Int32.TryParse(inputArray[1], out staffID))
                            {
                                Console.WriteLine("Officer ID not found");
                                break;
                            }
                            staffID_str = inputArray[1];

                            REMOVE(db, staffID_str);

                            break;

                        case "list":
                            if (inputArray.Length == 1)
                            {
                                LIST(db);
                            }
                            else if (inputArray.Length == 2)
                            {
                                LIST(db, inputArray[1]);
                            }
                            else
                            {
                                Console.WriteLine("The input must be either LIST or LIST <surname>");
                            }
                            break;

                        case "assign":

                            TOpos = Array.IndexOf(inputArray, "TO");
                            if (TOpos != 2)
                            {
                                Console.WriteLine("Ambulance ID is missing or not found");
                                break;
                            }

                            if (!Int32.TryParse(inputArray[1], out staffID))
                            {
                                Console.WriteLine("Officer ID not found");
                                break;
                            }
                            staffID_str = inputArray[1];

                            ambulanceID = inputArray[3];

                            ASSIGN(db, staffID_str, ambulanceID);

                            break;

                        case "unassign":
                            if (inputArray.Length != 2)
                            {
                                Console.WriteLine("The input must be a single 6 digit staff id number");
                                break;
                            }

                            if (!Int32.TryParse(inputArray[1], out staffID))
                            {
                                Console.WriteLine("Officer ID not found");
                                break;
                            }
                            staffID_str = inputArray[1];

                            UNASSIGN(db, staffID_str);

                            break;

                        case "exit":
                            running = false;
                            break;

                        default:
                            Console.WriteLine("Invalid command: the valid commands are ADD, REMOVE, LIST, ASSIGN, UNASSIGN and EXIT");
                            break;

                    }

                }
            }
        }

        static void ADD(AmbStaffContext db, string fNames, string lName, string sID, string sLevel)
        {
            var sm = new StaffMember {Surname = lName, FirstNames = fNames, OfficerID = sID, SkillLevel = sLevel, AssignedAmbulance = null };
            try
            {
                db.StaffMembers.Add(sm);
                db.SaveChanges();
                Console.WriteLine("The ambulance officer has been added");

            }
            catch(System.Data.Entity.Infrastructure.DbUpdateException)
            {
                Console.WriteLine("An error occured, the database was not updated");
            }

        }

        static void REMOVE(AmbStaffContext db, string sID)
        {
            var x = db.StaffMembers.Where(a => a.OfficerID == sID);
            if(x.Count() != 1)
            {
                Console.WriteLine("Officer ID not found");
                return;
            }

            var officer = x.First();
            try
            {
                db.StaffMembers.Remove(officer);
                db.SaveChanges();
                Console.WriteLine("Officer " + officer.FirstNames + " " + officer.Surname + " (" + officer.SkillLevel + ") has been removed");
            }
            catch
            {
                Console.WriteLine("An error has occured, officer not deleted");
            }
        }

        static void LIST(AmbStaffContext db)
        {
            DateTime dt = DateTime.Now;
            Console.WriteLine(String.Format("Ambulance officer list as of {0:dd MMM yyyy} at {0:h:mmtt}", dt));
            Console.WriteLine("Surname, First Name, Officer ID, Skill Level, Assigned Ambulance");
            foreach (var x in db.StaffMembers.OrderBy(s => s.Surname).ThenBy(f => f.FirstNames))
            {
                string assignedA = "";
                if (x.AssignedAmbulance == null) { assignedA = "None"; }
                else { assignedA = x.AssignedAmbulance; }
                Console.WriteLine(x.Surname + ", " + x.FirstNames + ", " + x.OfficerID + ", " + x.SkillLevel + ", " + assignedA);
            }
            Console.WriteLine("Listed " + db.StaffMembers.Count() + " officers");
        }

        static void LIST(AmbStaffContext db, string name)
        {
            DateTime dt = DateTime.Now;
            Console.WriteLine(String.Format("Ambulance officer list as of {0:dd MMM yyyy} at {0:h:mmtt}", dt));
            Console.WriteLine("Surname, First Name, Officer ID, Skill Level, Assigned Ambulance");
            foreach (var x in db.StaffMembers.Where(a => a.Surname == name).OrderBy(s => s.Surname).ThenBy(f => f.FirstNames))
            {
                string assignedA = "";
                if (x.AssignedAmbulance == null) { assignedA = "None"; }
                else { assignedA = x.AssignedAmbulance; }
                Console.WriteLine(x.Surname + ", " + x.FirstNames + ", " + x.OfficerID + ", " + x.SkillLevel + ", " + assignedA);
            }
            Console.WriteLine("Listed " + db.StaffMembers.Where(a => a.Surname == name).Count() + " officers");
        }

        static void ASSIGN(AmbStaffContext db, string sID, string ambID)
        {
            var x = db.StaffMembers.Where(a => a.OfficerID == sID);
            if (x.Count() != 1)
            {
                Console.WriteLine("Officer ID not found");
                return;
            }

            var officer = x.First();

            var y = db.Ambulances.Where(b => b.AmbulanceID == ambID);
            if (y.Count() != 1)
            {
                Console.WriteLine("Ambulance ID is missing or not found");
                return;
            }

            var ambulance = y.First();

            try
            {
                officer.AssignedAmbulance = ambulance.AmbulanceID;
                db.SaveChanges();
                Console.WriteLine("The ambulance officer has been assigned to " + ambulance.AmbulanceID + " at " + ambulance.Station);
            }
            catch
            {
                Console.WriteLine("An error has occured, officer not assigned to ambulance");
            }
        }

        static void UNASSIGN(AmbStaffContext db, string sID)
        {
            var x = db.StaffMembers.Where(a => a.OfficerID == sID);
            if (x.Count() != 1)
            {
                Console.WriteLine("Officer ID not found");
                return;
            }

            var officer = x.First();

            if(officer.AssignedAmbulance == null)
            {
                Console.WriteLine("Officer is not assigned to an ambulance");
                return;
            }

            try
            {
                var ambulance = db.Ambulances.Where(b => b.AmbulanceID == officer.AssignedAmbulance).First();
                officer.AssignedAmbulance = null;
                db.SaveChanges();
                Console.WriteLine("The ambulance officer has been removed from " + ambulance.AmbulanceID + " at " + ambulance.Station);
            }
            catch
            {
                Console.WriteLine("An error has occured, officer has not had ambulance unassigned");
            }
        }
    }


    public class AmbStaffContext : DbContext
    {
        public AmbStaffContext() : base("MySqlConnection") { }
        public DbSet<StaffMember> StaffMembers { get; set; }
        public DbSet<Ambulance> Ambulances { get; set; }
    }

    [Table("StaffMember")]
    public class StaffMember
    {
        public string Surname { get; set; }
        public string FirstNames { get; set; }
        [Key, DatabaseGenerated(DatabaseGeneratedOption.None)]
        public string OfficerID { get; set; }
        public string SkillLevel { get; set; }
        public string AssignedAmbulance { get; set; }
    }

    [Table("Ambulance")]
    public class Ambulance
    {
        [Key, DatabaseGenerated(DatabaseGeneratedOption.None)]
        public string AmbulanceID { get; set; }
        public string Station { get; set; }
    }
}
