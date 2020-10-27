import os

def filepath(no = 1):
    """
    
    :param no: no of files to be loaded
    :return: None
    """
    filepath_list = []
    count = 0
    while True:
        temp = input('Enter file path ending with /: ')
        
        # If empty space is entered by mistake
        if temp.lstrip() == '':
            continue
        elif not os.path.exists(temp):
            print('File path does not exist')
            continue
        else:
            filepath_list.append(temp)
            count += 1
            if count == no:
                break
                

    return filepath_list


if __name__=='__main__':

    num = int(input('Enter the number of directories: '))
    directories = filepath(num)
    print(directories)
