#! /var/bin/python3

from os import listdir
import datetime

import subprocess

sourcefile = 'template.html'
filename = 'uctenky.html'
billsdir = 'uctenky'

#fault fuelconsumption treshold
fault_consp_thld = 2/3

workdir='data/'

if __name__ == '__main__':

    #load original html file
    f = open(sourcefile,'r',encoding='utf-8')
    fdata = f.read()
    fdata = fdata.split('\n')
    f.close()

    #scan directory containing bills
    dirlist = listdir(billsdir)
    dirlist.sort(reverse=True)
    bills = []
    for fname in dirlist:
        try:
            sname = fname.split('.')[0].split('_')
            date = datetime.datetime.strptime(sname[0],'%Y%m%d').date()
            car = sname[1]
            vol = sname[2].split('l')
            vol = float('{}.{}'.format(vol[0],vol[1]))
            kmage = int(sname[3][:-2])
            bills.append([date,car,vol,kmage,fname])
        except:
            pass

    #sort data by car name
    auta = []
    spotreba = {}
    for bill in bills:
        if bill[1] not in spotreba:
            auta.append(bill[1])
            spotreba[bill[1]] = [[bill[0],bill[2],bill[3]],]
        else:
            spotreba[bill[1]].append([bill[0],bill[2],bill[3]])

    #calculate fuel comp. for cars
    for auto in auta:
        #print(auto)
        cnt = 0
        avg = 0
        # calculate fuel consumption 
        for i in range(len(spotreba[auto])):
            if i<(len(spotreba[auto])-1):
                spotreba[auto][i].append(spotreba[auto][i][2]-spotreba[auto][i+1][2])
                spotreba[auto][i].append(spotreba[auto][i][1]/(spotreba[auto][i][3]/100))
                avg+=spotreba[auto][i][-1]
                cnt+=1
        avg = avg/cnt
        #print(avg)
        
        rcnt = 0
        ravg = 0
        for row in spotreba[auto]:
            if (len(row)==5) and (row[4]<(avg*fault_consp_thld)):
                del(row[-1])
                del(row[-1])
            if (len(row)==5):
                ravg+=row[4]
                rcnt+=1
            #print(row)

        ravg = ravg/rcnt
        #print(ravg)

        #save data form plotting
        fname = '{}{}_data.txt'.format(workdir,auto)
        f = open(fname,'w')
        f.write('# date; fuel consumption[l/100km]\n')
        for raw in spotreba[auto]:
            try:
                f.write('{:04}{:02}{:02}; {:0.2f}\n'.format(raw[0].year,raw[0].month,raw[0].day,raw[4]))
            except:
                f.write('{:04}{:02}{:02}; NaN\n'.format(raw[0].year,raw[0].month,raw[0].day))
        f.close()

    # create gnuplot script
    fname = '{}plotit.gp'.format(workdir)
    f = open(fname,'w')
    f.write('#! /usr/bin/gnuplot\n\n')
    f.write('# this script plots fuel consumption from files\n# is\'s probably automatically generated just before plotting so it doesn\'t make\n# a big sence to modify it\n# running the script: gnuplot plotit.gp\n\n')
    f.write('set xdata time\n')
    f.write('set style data lines\n')
    f.write('unset multiplot\n')
    f.write('set term png size 800,400\n')
    f.write('set timefmt "%Y%m%d"\n')
    f.write('set format x "%m/%y"\n')
    f.write('set ylabel "l/100km"\n')
    f.write('set autoscale y\n')
    f.write('set autoscale x\n')
    f.write('set output \'{}chart.png\'\n'.format(workdir))
    f.write('set datafile separator \';\'\n')
    f.write('set grid\n')
    f.write('plot ')
    afirst = True
    for auto in auta:
        if afirst:
            afirst=False
        else:
            f.write(', \\\n     ')
        f.write('\'{}{}_data.txt\' using 1:2 t \'{}\' w linespoints linewidth 2.5'.format(workdir,auto,auto))
    f.write('\n')
    f.close()

    # run gnuplot script
    print('Generating chart ... ',end='')
    if subprocess.call('gnuplot {}plotit.gp'.format(workdir),shell=True)==0:
          print('OK')
    else:
          print('Error')

    # parse html file
    f = open(filename,'w',encoding='utf-8')
    copynow = True
    
    for line in fdata:
        if copynow: #seek automated section (and copy)
            f.write('{}\n'.format(line))

            #seek table section
            p = line.find('<!-- tabulka uctenky -->')
            if p!=-1: #found table section
                stepstr = line[:p]
                cnt = 1
                f.write('\n{}<table>\n'.format(stepstr))
                f.write('{}\t<tr><th>pořadí</th><th>datum</th><th>auto</th><th>najeto</th><th>natankováno</th></tr>\n'.format(stepstr))
                for bill in bills:
                    f.write('{}\t<tr><th><a href="#bill{}">{}</a></th><td>{}</td><td>{}</td><td>{} km</td><td>{} l</td></tr>\n'.format(stepstr,cnt,cnt,bill[0],bill[1],bill[3],bill[2]))
                    cnt += 1
                f.write('{}</table>\n'.format(stepstr))
                copynow=False

            #seek images section
            p = line.find('<!-- sekce uctenky -->')
            if p!=-1:
                stepstr = line[:p]
                cnt = 1
                odd = True
                f.write('\n')
                for bill in bills:
                    f.write('{}<a name="bill{}"></a>\n'.format(stepstr,cnt))
                    if odd:
                        f.write('{}<figure class="left">\n'.format(stepstr))
                    else:
                        f.write('{}<figure class="right">\n'.format(stepstr))                        
                    f.write('{}\t<a href="uctenky/{}"><img class="full" src="uctenky/{}" alt="{} {}l {}km"></a>\n'.format(stepstr,bill[4],bill[4],bill[1],bill[2],bill[3]))
                    f.write('{}\t<figcaption><b>{}</b>) {} {} {}l {}km</figcaption>\n'.format(stepstr,cnt,bill[0],bill[1],bill[2],bill[3]))
                    f.write('{}</figure>\n\n'.format(stepstr))
                    if not odd:
                        f.write('{}<img class="divider" src="files/divider.png">\n\n'.format(stepstr))
                    odd = not odd
                    cnt+=1
                copynow=False
                
        else: #skip to end of automated section (not copy)
            p = line.find('<!-- konec ')
            if p!=-1: #found end of automated section
                f.write('{}\n'.format(line))
                copynow=True

    f.close()
    
    #for bill in bills:
    #    print(bill)
